import io
import math
import json
import xedocs
import rframe
import datetime
import pydantic
import logging

import numpy as np
import pandas as pd
import panel as pn

import param

from typing import Any, ClassVar, List, Type

try:
    from typing import _LiteralGenericAlias
except ImportError:
    _LiteralGenericAlias = None

from panel.widgets import (
    LiteralInput,
    CompositeWidget,
    DatetimeRangePicker,
    EditableRangeSlider,
)

from panel.layout import ListPanel, Column
from panel.io.server import unlocked
from tornado.ioloop import IOLoop

from pydantic_panel import infer_widget, PydanticModelEditor, ItemListEditor

from pydantic_panel.dispatchers import clean_kwargs

from typing import ClassVar, Type


from concurrent.futures import ThreadPoolExecutor

from .schemas import XeDoc
from .utils import docs_to_wiki, docs_to_dataframe
from .dispatchers import json_serializable

executor = ThreadPoolExecutor(max_workers=5)  # pylint: disable=consider-using-with
logger = logging.getLogger(__name__)


def make_csv(schema, docs, fields=None):
    df = docs_to_dataframe(schema, docs, columns=fields)
    return io.StringIO(df.to_csv())


def make_json(schema, docs, fields=None):
    if fields is not None:
        fields = set(fields)
    docs = [json.loads(doc.json(include=fields)) for doc in docs]

    return io.StringIO(json.dumps(docs, indent=4))


def make_wiki(schema, docs, fields=None):
    return io.StringIO(docs_to_wiki(schema, docs, columns=fields))


download_options = {
    "csv": make_csv,
    "json": make_json,
    "wiki": make_wiki,
}


class NullableInput(LiteralInput):
    def _process_property_change(self, msg):
        # msg = Widget._process_property_change(self, msg)
        if "value" in msg and msg["value"] == "":
            msg["value"] = "null" if self.serializer == "json" else "None"

        msg = super()._process_property_change(msg)
        return msg


class TimeIntervalEditor(DatetimeRangePicker):
    value = param.ClassSelector(rframe.TimeInterval, default=None)

    def _serialize_value(self, value):
        value = super()._serialize_value(value)
        if any([v is None for v in value]):
            return None
        return rframe.TimeInterval(left=value[0], right=value[1])

    def _deserialize_value(self, value):
        if isinstance(value, rframe.TimeInterval):
            value = value.left, value.right

        value = super()._deserialize_value(value)
        return value

    @param.depends("start", "end", watch=True)
    def _update_value_bounds(self):
        pass


@infer_widget.dispatch(precedence=2)
def infer_widget(value: rframe.TimeInterval, field: Any, **kwargs):
    kwargs = clean_kwargs(TimeIntervalEditor, kwargs)
    return TimeIntervalEditor(value=value, **kwargs)


class IntegerIntervalEditor(EditableRangeSlider):

    step = param.Integer(default=1, constant=True)

    format = param.String(default="0", constant=True)

    value = param.ClassSelector(rframe.IntegerInterval, default=None)

    value_throttled = param.ClassSelector(rframe.IntegerInterval, default=None)

    @param.depends("value", watch=True)
    def _update_value(self):
        if self.value is None:
            return

        self._slider.value = (self.value.left, self.value.right)
        self._start_edit.value = self.value.left
        self._end_edit.value = self.value.right

    def _sync_value(self, event):
        with param.edit_constant(self):
            new_value = rframe.IntegerInterval(left=event.new[0], right=event.new[1])
            self.param.update(**{event.name: new_value})

    def _sync_start_value(self, event):
        if event.name == "value":
            end = self.value.right if self.value else self.end
        else:
            end = self.value_throttled.right if self.value_throttled else self.end

        new_value = rframe.IntegerInterval(left=event.new, right=end)

        with param.edit_constant(self):
            self.param.update(**{event.name: new_value})

    def _sync_end_value(self, event):
        if event.name == "value":
            start = self.value.left if self.value else self.start
        else:
            start = self.value_throttled.left if self.value_throttled else self.start

        new_value = rframe.IntegerInterval(left=start, right=event.new)
        with param.edit_constant(self):
            self.param.update(**{event.name: new_value})


@infer_widget.dispatch(precedence=2)
def infer_widget(value: rframe.IntegerInterval, field: Any, **kwargs):
    start = None
    end = None

    if start is None:
        start = kwargs.get("start", value._min if value is not None else 0)

    if end is None:
        end = kwargs.get("end", value._max if value is not None else 1)

    step = value._resolution if value else 1

    kwargs = clean_kwargs(IntegerIntervalEditor, kwargs)
    return IntegerIntervalEditor(value=value, step=step, start=start, end=end, **kwargs)


class XeDocEditor(PydanticModelEditor):

    _trigger_recreate = ["class_", "allow_save", "allow_delete"]

    datasource = param.Parameter(default=None)
    class_ = param.ClassSelector(class_=XeDoc, is_instance=False)
    value = param.ClassSelector(class_=XeDoc)

    pre_save = param.HookList([])
    post_save = param.HookList([])
    pre_delete = param.HookList([])
    post_delete = param.HookList([])

    delete_requested = param.Boolean(False)
    deleted = param.Boolean(False)
    deletion_error = param.String("")

    allow_save = param.Boolean(True)

    allow_delete = param.Boolean(True)

    add_debugger = param.Boolean(False)

    def __init__(self, **params):
        if params.get("fields", None) is None:
            schema = params.get("class_", None) or params.get("value", None)
            if schema is not None:
                index_fields = list(schema.get_index_fields())
                column_fields = list(schema.get_column_fields())
                params["fields"] = index_fields + column_fields

        super().__init__(**params)

    def _update_save_button(self, target, event):
        target.disabled = event.new is None

    @property
    def can_delete(self):
        if self.deleted or self.value is None:
            return False
        try:
            self.value.pre_delete(self.datasource)
            return True
        except:
            return False

    def _save_clicked(self, event):
        if self.value is None:
            return

        event.obj.name = "Saving..."
        self.loading = True
        try:
            doc = self.value
            for cb in self.pre_save:
                cb(doc)

            doc.save(self.datasource)

            for cb in self.post_save:
                cb(doc)
        finally:
            self.loading = False
            event.obj.name = "Save"

    @pn.depends("deleted", "delete_requested")
    def delete_button(self):
        if self.deleted:
            return pn.widgets.Button(name="Deleted.", disabled=True)

        if self.delete_requested:
            cancel = pn.widgets.Button(
                name="❌ Cancel",
            )

            def cancel_cb(event):
                self.delete_requested = False

            cancel.on_click(cancel_cb)

            confirm = pn.widgets.Button(
                name="⚠️ Confirm? This cannot be undone. ⚠️",
                button_type="danger",
                width_policy="max",
            )

            def confirm_cb(event):
                confirm.disabled = True
                try:
                    self.delete()
                finally:
                    confirm.disabled = False

            confirm.on_click(confirm_cb)

            return pn.Column(cancel, confirm)

        delete = pn.widgets.Button(
            name="Delete 🗑️", button_type="danger", width_policy="max"
        )

        def delete_cb(event):
            self.delete_requested = True

        delete.on_click(delete_cb)

        if self.deletion_error:
            error_message = pn.pane.Alert(self.deletion_error, alert_type="danger")
            acknowledge = pn.widgets.Button(
                name="✔️ OK",
            )

            def ack_cb(event):
                self.deletion_error = ""

            acknowledge.on_click(ack_cb)

            return pn.Column(error_message, acknowledge)

        return delete

    def delete(self):
        self.loading = True
        try:
            doc = self.value

            for cb in self.pre_delete:
                cb(doc)

            doc.delete(self.datasource)
            self.deleted = True

            for cb in self.post_delete:
                cb(doc)
        except Exception as e:
            self.deletion_error = str(e)
            logger.error(str(e))
        finally:
            self.loading = False

    def _add_buttons(self):

        if self.allow_save:
            save_button = pn.widgets.Button(
                name="Save 💾", button_type="success", disabled=self.value is None
            )
            self.link(save_button, callbacks={"value": self._update_save_button})
            save_button.on_click(self._save_clicked)
            self._composite.append(save_button)

        if self.allow_delete and self.can_delete:
            self._composite.append(self.delete_button)

        if self.add_debugger:
            debugger = pn.widgets.Debugger(name="Debugger", width_policy="max")
            self._composite.append(debugger)

    def _recreate_widgets(self, *events):
        super()._recreate_widgets(*events)
        self._add_buttons()


@infer_widget.dispatch(precedence=2)
def infer_widget(value: XeDoc, field: Any, **kwargs):
    if field is not None:
        kwargs["name"] = kwargs.pop("name", field.name)
    kwargs = clean_kwargs(XeDocEditor, kwargs)
    return XeDocEditor(value=value, **kwargs)


class QueryEditor(CompositeWidget):

    _composite_type = pn.Column

    _trigger_recreate: ClassVar[List] = ["class_", "extra_widgets", "fields"]

    class_ = param.ClassSelector(XeDoc, is_instance=False)

    value = param.Dict({})

    _widgets = param.Dict({})

    fields = param.List()

    extra_widgets = param.List([])

    by_alias = param.Boolean(False)

    def __init__(self, **params):
        super().__init__(**params)
        self._update_layout()
        self.param.watch(self._update_layout, self._trigger_recreate)

    def _widget_for(self, field_name):
        field = self.class_.__fields__[field_name]

        alias = field.alias if self.by_alias else field_name

        alias = alias.replace("_", " ").capitalize()

        if type(field.outer_type_) == _LiteralGenericAlias:
            options = list(field.outer_type_.__args__)
            widget = pn.widgets.MultiChoice(name=alias + "s", value=[], options=options)
        else:
            try:
                widget = ItemListEditor(
                    value=[],
                    class_=field.outer_type_,
                    item_field=field,
                    name=alias + "s",
                )
            except:
                widget = NullableInput(
                    value=None,
                    name=alias,
                )

        widget.param.watch(self._validate_field, "value")
        return widget

    def _make_widgets(self):
        fields = self.fields or list(self.class_.get_index_fields())
        self._widgets = {
            field_name: self._widget_for(field_name) for field_name in fields
        }

    def _update_layout(self, *events):
        if self.class_ is None:
            return

        self._make_widgets()

        self._composite[:] = list(self._widgets.values())

        for w in self.extra_widgets:
            self._composite.append(w)

    def _validate_field(self, event):

        for name, widget in self._widgets.items():
            if event.obj == widget:
                break
        else:
            return

        index = self.class_.index_for(name)

        label = index.validate_label(event.new)

        if label:
            self.value[name] = label
        else:
            self.value[name] = None

        self.param.trigger("value")


class XeDocListEditor(CompositeWidget):
    """Composite widget for editing a list of XeDocs"""

    _composite_type: ClassVar[Type[ListPanel]] = Column

    row_size = param.Integer(30)
    MAX_DISPLAY_ROWS = 20
    MAX_SEND_ROWS = 500
    column_size = param.Integer(100)

    page_size = param.Integer(15)

    class_ = param.ClassSelector(XeDoc, is_instance=False)

    pagination = param.ObjectSelector(
        default=None, allow_None=True, objects=["local", "remote"]
    )

    value = param.List(default=[], class_=XeDoc)

    table_widget = param.Parameter(default=None)

    def __init__(self, **params):
        super().__init__(**params)
        if self.class_ is None and self.value:
            self.class_ = self.value[0].__class__
        self._composite[:] = [pn.panel(self.table_view)]

    @param.depends("class_", "pagination", "page_size", watch=True, on_init=True)
    def _make_table_widget(self):

        if len(self.value) > self.MAX_SEND_ROWS:
            self.pagination = "remote"

        elif len(self.value) > self.MAX_DISPLAY_ROWS:
            self.pagination = "local"

        docs = [json_serializable(doc.index_labels) for doc in self.value]

        if self.class_ is not None:
            df = pd.DataFrame(docs, columns=list(self.class_.get_index_fields()))
            nwidgets = len(self.class_.get_column_fields()) + 2
            ncols = len(self.class_.get_index_fields()) + 2

        else:
            df = pd.DataFrame()
            nwidgets = 2
            ncols = 3

        nrows = max(self.MAX_DISPLAY_ROWS, nwidgets) + 1

        self.table_widget = pn.widgets.Tabulator(
            df,
            name="Data (Click to edit)",
            disabled=True,
            row_content=self._value_editor,
            sizing_mode="stretch_both",
            min_height=nrows * self.row_size,
            min_width=ncols * self.column_size,
            width_policy="max",
            height_policy="max",
            embed_content=False,
            page_size=self.page_size,
            pagination=self.pagination,
            show_index=False,
        )

    @param.depends(
        "value",
        watch=True,
    )
    def _update_table(self):

        if len(self.value) > self.MAX_SEND_ROWS:
            self.pagination = "remote"

        elif len(self.value) > self.MAX_DISPLAY_ROWS:
            self.pagination = "local"

        if self.table_widget is None:
            return

        if not len(self.table_widget.value) or not self.value:
            return self._make_table_widget()

        assert all(
            [isinstance(doc, self.class_) for doc in self.value]
        ), f"Value must be a list of {self.class_} instances"

        docs = [json_serializable(doc.index_labels) for doc in self.value]

        df = pd.DataFrame(docs, columns=list(self.class_.get_index_fields()))
        self.table_widget.value = df

    @pn.depends("table_widget")
    def table_view(self):
        if self.table_widget is None:
            return pn.Column()
        return pn.Column(self.table_widget)

    def _value_editor(self, row):
        if len(self.value) <= row.name:
            return pn.Column()

        doc = self.value[row.name]

        columns = list(doc.get_column_fields())

        editor = XeDocEditor(
            value=doc,
            class_=self.class_,
            fields=columns,
            allow_delete=True,
        )

        def cb(event):
            if event.new:
                self.value.pop(row.name, None)
                self.param.trigger("value")

        editor.param.watch(cb, "deleted")

        return pn.Column(editor)


@infer_widget.dispatch(precedence=2)
def infer_widget(value: List[XeDoc], field, **kwargs):
    if field is not None:
        kwargs["class_"] = kwargs.pop("class_", field.type_)

    kwargs = clean_kwargs(XeDocListEditor, kwargs)

    return XeDocListEditor(value=value, **kwargs)


class ModelTableEditor(pn.viewable.Viewer):

    class_ = param.ClassSelector(pydantic.BaseModel, is_instance=False)

    docs = param.List(class_=pydantic.BaseModel)

    query_editor = param.ClassSelector(QueryEditor)
    model_editor = param.ClassSelector(XeDocEditor)

    query = param.Dict({})

    page = param.Integer(-1, bounds=(-1, 1))
    last_page = param.Integer(0)
    page_size = param.Integer(15)

    refresh_table = param.Event()
    table = param.Parameter()

    def __init__(self, **params):
        super().__init__(**params)

        self.inc_page = pn.widgets.Button(
            name="\u25b6",
            disabled=(self.page >= self.last_page or self.page == -1),
            height=50,
            max_width=50,
            align="center",
        )
        self.inc_page.on_click(self.increment_page)

        self.dec_page = pn.widgets.Button(
            name="\u25c0",
            disabled=self.page <= 0,
            align="center",
            height=50,
            width=50,
        )
        self.dec_page.on_click(self.decrement_page)

        self.find_button = pn.widgets.Button(
            name="🔍 Query", button_type="primary", align="center"
        )

        self.find_button.on_click(self.filter_callback)

        self.param.watch(
            self._update_docs, ["class_", "page", "query", "refresh_table"]
        )

    @param.depends("class_", watch=True, on_init=True)
    def _make_table_widget(self):
        docs = [json_serializable(doc.index_labels) for doc in self.docs]
        df = pd.DataFrame(docs, columns=list(self.class_.get_index_fields()))

        self.table = pn.widgets.Tabulator(
            df,
            name="Data (Click to edit)",
            disabled=True,
            row_content=self.value_editor,
            sizing_mode="stretch_both",
            embed_content=False,
            show_index=False,
            #  width=1000,
            min_height=500,
        )

        self.query_editor = QueryEditor(class_=self.class_)

        self.model_editor = XeDocEditor(class_=self.class_, allow_delete=False)
        self.model_editor.post_save.append(self._update_docs)

    @param.depends("docs", watch=True)
    def _docs_changed(self):
        if self.table is None:
            self._make_table_widget()
            return

        if not len(self.table.value):
            return self._make_table_widget()

        docs = [json_serializable(doc.index_labels) for doc in self.docs]
        df = pd.DataFrame(docs, columns=list(self.class_.get_index_fields()))
        self.table.value = df
        self.table.loading = False

    @param.depends("page", watch=True)
    def _page_changed(self):
        self.inc_page.disabled = self.page >= self.last_page or self.page == -1
        self.dec_page.disabled = self.page <= 0

    @param.depends("last_page", watch=True)
    def _last_page_changed(self):
        self.inc_page.disabled = self.page >= self.last_page or self.page == -1

    def filter_callback(self, event):
        query = {k: v for k, v in self.query_editor.value.items() if v}
        query = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

        if self.query != query:
            self.query = query
            self.page = 0
        if self.page == -1:
            self.page = 0
        # end = math.ceil(self.class_.compile_query(**self.query).count()/self.page_size)
        # self.param.page.bounds = (0, end)
        # self.last_page = end
        self._update_page_range()
        self._update_docs()

    def trigger_refresh_cb(self, event):
        self.refresh_table = True

    def increment_page(self, event):
        self.page += 1

    def decrement_page(self, event):
        self.page -= 1

    def _set_page_range(self, future):
        count = future.result()
        last_page = math.ceil(count / self.page_size)
        with unlocked():
            self.param.page.bounds = (0, last_page)
            self.last_page = last_page

    def _set_docs(self, future):
        docs = future.result()

        if docs == self.docs:
            self.table.loading = False

        with unlocked():
            self.docs = docs
            docs = [json_serializable(doc.index_labels) for doc in self.docs]

    def _get_page(self):
        skip = self.page * self.page_size
        docs = []
        try:
            docs = self.class_.find(**self.query, _skip=skip, _limit=self.page_size)
        except Exception as e:
            logger.error(str(e))

        return docs

    def _get_page_count(self):
        count = 1
        try:
            count = self.class_.compile_query(**self.query).count()
        except Exception as e:
            logger.error(str(e))
        return count

    def _update_docs(self, *events):
        self.table.loading = True
        loop = IOLoop.current()
        future = executor.submit(self._get_page)
        loop.add_future(future, self._set_docs)

    def _update_page_range(self, *events):
        self.table.loading = True
        loop = IOLoop.current()
        future = executor.submit(self._get_page_count)
        loop.add_future(future, self._set_page_range)

    def value_editor(self, row):
        if len(self.docs) <= row.name:
            return pn.Column()

        doc = self.docs[row.name]

        columns = list(doc.get_column_fields())

        editor = XeDocEditor(
            value=doc,
            class_=self.class_,
            fields=columns,
            allow_delete=True,
        )

        editor.post_delete.append(self._update_docs)

        return pn.Column(editor)

    @pn.depends("table")
    def table_panel(self):
        if self.table is None:
            return pn.Column()
        return pn.Column(
            self.table,
            sizing_mode="stretch_width",
            #  width=1000,
            scroll=False,
        )

    @pn.depends("page", "last_page")
    def page_controls(self):
        end = self.last_page or 1

        page_view = pn.indicators.LinearGauge(
            name="Page",
            value=self.page,
            bounds=(0, end),
            format="{value}",
            horizontal=True,
            width=75,
            min_height=75,
            align="end",
            tick_size="12px",
            title_size="12px",
            value_size="12px",
        )
        return pn.Row(
            self.dec_page, page_view, self.inc_page, max_width=600, width_policy="max"
        )

    @pn.depends("query_editor")
    def query_panel(self):
        if self.query_editor is None:
            return pn.Column()
        return pn.Column(self.query_editor)

    def controls_panel(self):
        query_container = pn.Card(
            "Valid JSON or python literals",
            self.query_panel,
            header=pn.Row("🔍 Filter Documents", pn.layout.Spacer(), width=300),
            collapsed=True,
        )

        add_new = pn.Card(
            self.new_doc_panel,
            name="insert_new",
            header=pn.Row("➕ New Document", pn.layout.Spacer(), width=300),
            collapsed=True,
        )

        return pn.Column(
            query_container,
            self.find_button,
            pn.layout.Divider(),
            add_new,
        )

    @pn.depends("model_editor")
    def new_doc_panel(self):
        if self.model_editor is None:
            return pn.Column()
        return pn.Column(self.model_editor, width_policy="min")

    @pn.depends("class_")
    def download_panel(self):

        current_only = pn.widgets.RadioBoxGroup(
            options={"Current page": 1, "Entire query": 0}, inline=True
        )
        filename = pn.widgets.TextInput(name="Filename", value=self.class_._ALIAS)

        filetype = pn.widgets.Select(name="Format", options=list(download_options))

        fields = pn.widgets.MultiChoice(name='Fields', value=list(self.class_.__fields__),
                    options=list(self.class_.__fields__))

        def cb():
            if current_only.value:
                docs = self.docs
            else:
                docs = self.class_.find(**self.query)
            
            return download_options[filetype.value](self.class_, docs, 
                                                    fields=fields.value)

        download_button = pn.widgets.FileDownload(
            filename=f"{self.class_._ALIAS}.{filetype.value}", callback=cb
        )

        def update_filename(*events):
            download_button.filename = f"{filename.value}.{filetype.value}"

        filename.param.watch(update_filename, "value")
        filetype.param.watch(update_filename, "value")

        return pn.Column(current_only, fields, 
                         filename, filetype, 
                         download_button)

    def __panel__(self):
        right_panel = pn.Column(self.page_controls, self.table_panel)
        left_panel = self.controls_panel
        return pn.Row(
            left_panel, right_panel, scroll=False, sizing_mode="stretch_width"
        )


class XedocsEditor(pn.viewable.Viewer):
    _schemas_by_category = xedocs.schemas_by_category()

    selection_layout = param.ClassSelector(
        class_=ListPanel, is_instance=False, default=pn.Row
    )

    category = param.Selector(objects=list(_schemas_by_category))
    collection = param.Selector(objects=[None])

    editor = param.ClassSelector(ModelTableEditor)

    def __init__(self, **params):
        all_schemas = xedocs.schemas_by_category()
        schemas = params.pop("schemas", None)
        if schemas is None:
            schemas = xedocs.list_schemas()

        # if isinstance(schemas, dict):
        #     self._all_schemas = schemas
        #

        categories = params.pop("categories", None)

        if categories is None:
            categories = list(xedocs.schemas_by_category())

        schemas_by_category = {}
        for category in categories:
            cat_schemas = all_schemas.get(category, {})
            schema_dict = {k: v for k, v in cat_schemas.items() if k in schemas}
            schemas_by_category[category] = schema_dict

        self._schemas_by_category = schemas_by_category
        self.param.category.objects = list(schemas_by_category)
        super().__init__(**params)

    @param.depends("category", watch=True, on_init=True)
    def _category_changed(self):
        schemas = self._schemas_by_category.get(self.category, {})
        if not schemas:
            return

        objects = list(schemas.values())
        self.param.collection.names = schemas
        self.param.collection.objects = objects
        self.collection = objects[0]

    @param.depends("collection", watch=True, on_init=True)
    def _selection_changed(self):
        if self.collection is None:
            return
        self.editor = ModelTableEditor(class_=self.collection)

    @pn.depends("selection_layout")
    def selection_panel(self):
        return self.selection_layout(self.param.category, self.param.collection)

    @pn.depends("editor")
    def query_or_insert_panel(self):
        if self.editor is None:
            return pn.Column()
        return pn.panel(self.editor.controls_panel)

    @pn.depends("editor")
    def query_panel(self):
        if self.editor is None:
            return pn.Column()

        return pn.Column(
            "### Filters (python literals)", self.editor.query_panel, width_policy="max"
        )

    @pn.depends("editor")
    def new_doc_panel(self):
        if self.editor is None:
            return pn.Column()
        return pn.panel(self.editor.new_doc_panel)

    @pn.depends("editor")
    def data_panel(self):
        if self.editor is None:
            return pn.Column()
        return pn.Column(self.editor.page_controls, self.editor.table_panel)

    @pn.depends("editor")
    def find_button_panel(self):
        if self.editor is None:
            return pn.Row(pn.layout.Spacer(width_policy="max"))
        return pn.Row(
            pn.layout.Spacer(width_policy="max"),
            self.editor.find_button,
            pn.layout.Spacer(width_policy="max"),
        )

    @pn.depends("editor")
    def download_panel(self):
        if self.editor is None:
            return pn.Row(pn.layout.Spacer(width_policy="max"))
        return pn.panel(self.editor.download_panel)

    def __panel__(self):
        bottom_panel = pn.Row(self.query_or_insert_panel, self.data_panel)
        return pn.Column(self.selection_panel, pn.layout.Divider(), bottom_panel)
