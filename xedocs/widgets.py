import math
import xedocs
import rframe
import datetime
import pydantic


import numpy as np
import pandas as pd
import panel as pn

import param

from typing import Any, ClassVar, List, Type

from panel.widgets import (CompositeWidget, 
                           DatetimeRangePicker, 
                           EditableRangeSlider)

from panel.layout import ListPanel, Column
from panel.io.server import unlocked
from tornado.ioloop import IOLoop

from pydantic_panel import (get_widget, 
                            json_serializable, 
                            PydanticModelEditor)
from pydantic_panel.dispatchers import clean_kwargs

from panel.widgets.slider import _SliderBase
from bokeh.models.widgets import RangeSlider as _BkRangeSlider
from bokeh.model import Model

from typing import Mapping, ClassVar, Type


from concurrent.futures import ThreadPoolExecutor

from .schemas import XeDoc


executor = ThreadPoolExecutor(max_workers=2)  # pylint: disable=consider-using-with

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
    
    @param.depends('start', 'end', watch=True)
    def _update_value_bounds(self):
        pass

@get_widget.dispatch(precedence=2)
def get_widget(value: rframe.TimeInterval, field: Any, **kwargs):
    kwargs = clean_kwargs(TimeIntervalEditor, kwargs)
    return TimeIntervalEditor(value=value, **kwargs)


class IntegerIntervalEditor(EditableRangeSlider):
    
    step = param.Integer(default=1, constant=True)
    
    format = param.String(default='0', constant=True)
    
    value = param.ClassSelector(rframe.IntegerInterval, 
                                default=None)
    
    value_throttled = param.ClassSelector(rframe.IntegerInterval, 
                                default=None)

    @param.depends('value', watch=True)
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
        if event.name == 'value':
            end = self.value.right if self.value else self.end
        else:
            end = self.value_throttled.right if self.value_throttled else self.end
            
        new_value = rframe.IntegerInterval(left=event.new, right=end)
        
        with param.edit_constant(self):
            self.param.update(
                **{event.name: new_value}
            )

    def _sync_end_value(self, event):
        if event.name == 'value':
            start = self.value.left if self.value else self.start
        else:
            start = self.value_throttled.left if self.value_throttled else self.start
            
        new_value = rframe.IntegerInterval(left=start, right=event.new)
        with param.edit_constant(self):
            self.param.update(
                **{event.name: new_value}
            )
            

@get_widget.dispatch(precedence=2)
def get_widget(value: rframe.IntegerInterval, field: Any, **kwargs):
    start = None
    end = None

    if start is None:
        start = kwargs.get('start', value._min if value is not None else 0)
    
    if end is None:
        end = kwargs.get('end', value._max if value is not None else 1)
    
    step = value._resolution if value else 1

    kwargs = clean_kwargs(IntegerIntervalEditor, kwargs)
    return IntegerIntervalEditor(value=value, step=step,
                                 start=start, end=end, **kwargs)


class XeDocEditor(PydanticModelEditor):

    _trigger_recreate = ['class_', 
                         'allow_save', 'allow_delete']

    datasource = param.Parameter(default=None)
    class_ = param.ClassSelector(class_=XeDoc, is_instance=False)
    value = param.ClassSelector(class_=XeDoc)

    pre_save = param.HookList([])
    post_save = param.HookList([])
    pre_delete = param.HookList([])
    post_delete = param.HookList([])

    deleted = param.Boolean(False)

    allow_save = param.Boolean(True)

    allow_delete = param.Boolean(True)
    
    add_debugger = param.Boolean(False)
    
    def __init__(self, **params):
        if params.get('fields', None) is None:
            schema = params.get('class_', None) or params.get('value', None)
            if schema is not None:
                index_fields = list(schema.get_index_fields())
                column_fields = list(schema.get_column_fields())
                params['fields'] = index_fields + column_fields

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

        event.obj.name = 'Saving...'
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
            event.obj.name = 'Save'

    def _delete_clicked(self, event):
        if event.obj.name == 'Delete':
            event.obj.name = 'Confirm?'
            return
        
        event.obj.name = 'Deleting...'
        self.loading = True
        try:
            doc = self.value

            for cb in self.pre_delete:
                cb(doc)
                
            doc.delete(self.datasource)
            self.deleted = True
            
            for cb in self.post_delete:
                cb(doc)
        finally:
            self.loading = False
            event.obj.name = 'Deleted.'
            
    def _add_buttons(self):
        
        if self.allow_save:
            save_button = pn.widgets.Button(name='Save 💾',
                                            button_type='success',
                                            disabled=self.value is None)
            self.link(save_button,
                      callbacks={'value': self._update_save_button})
            save_button.on_click(self._save_clicked)
            self._composite.append(save_button)
            
        if self.allow_delete and self.can_delete:
            delete_button = pn.widgets.Button(name='Delete 🗑️', button_type='danger')
            delete_button.on_click(self._delete_clicked)
            self._composite.append(delete_button)

        if self.add_debugger:
            debugger = pn.widgets.Debugger(name='Debugger', width_policy='max')
            self._composite.append(debugger)

    def _recreate_widgets(self, *events):
        super()._recreate_widgets(*events)
        self._add_buttons()


@get_widget.dispatch(precedence=2)
def get_widget(value: XeDoc, field: Any, **kwargs):
    if field is not None:
        kwargs['name'] = kwargs.pop('name', field.name)
    kwargs = clean_kwargs(XeDocEditor, kwargs)
    return XeDocEditor(value=value, **kwargs)


class QueryEditor(CompositeWidget):

    _composite_type = pn.Column

    _trigger_recreate:  ClassVar[List] = ['class_', 'extra_widgets', 'fields']

    class_ = param.ClassSelector(XeDoc, is_instance=False)

    value = param.Dict({})
            
    _widgets = param.Dict({})

    fields = param.List()

    extra_widgets = param.List([])

    by_alias = param.Boolean(False)
    
    def __init__(self, **params):
        super().__init__(**params)
        self._update_layout()
        self.param.watch(self._update_layout,
                         self._trigger_recreate)

    def _widget_for(self, field_name):
        field = self.class_.__fields__[field_name]
            
        value = self.value.get(field_name, None)

        if value is None:
            value = field.default

        value = json_serializable(value)

        alias = field.alias if self.by_alias else field_name

        alias = alias.replace('_', ' ').capitalize()
        widget = pn.widgets.LiteralInput(value=value,
                                            name=alias,)
        widget.param.watch(self._validate_field, 'value')
        return widget

    def _make_widgets(self):
        fields = self.fields or list(self.class_.get_index_fields())
        self._widgets = {field_name: self._widget_for(field_name)
                         for field_name  in fields}

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

        self.value[name] = label

        self.param.trigger('value')

class XeDocListEditor(CompositeWidget):
    """Composite widget for editing a list of XeDocs"""

    _composite_type: ClassVar[Type[ListPanel]] = Column

    _updating_item = param.Boolean(False)

    row_size = param.Integer(50)

    datasource = param.Parameter(default=None)

    class_ = param.ClassSelector(XeDoc, is_instance=False)

    value = param.List(default=[], class_=XeDoc)

    def __init__(self, **params):
        super().__init__(**params)

        if self.class_ is None and self.value:
            self.class_ = self.value[0].__class__

        self._update_widgets()
        self.param.watch(self._update_widgets, "class_")
        self.param.watch(self._update_table, "value")

    def _value_editor(self, row):
        if len(self.value)<=row.name:
            return pn.Column()

        doc = self.value[row.name]

        columns = list(doc.get_column_fields())

        editor = XeDocEditor(value=doc,
                             datasource=self.datasource,
                             class_=self.class_,
                             fields=columns,
                             allow_delete=True,
                             show_debugger=False)
        def cb(event):
            if event.new:
                self.value.pop(row.name, None)
                self.param.trigger('value')

        editor.param.watch(cb, 'deleted')

        return pn.Column(editor)

    def _update_table(self, *events):
        docs = [json_serializable(doc.index_labels)
                for doc in self.value]
        df = pd.DataFrame(docs,
                          columns=list(self.class_.get_index_fields()))
        self.table.value = df

    def _make_table(self):
        docs = [json_serializable(doc.index_labels)
                for doc in self.value]
        if self.class_:
            df = pd.DataFrame(docs, 
                              columns=list(self.class_.get_index_fields()))
        else:
            df = pd.DataFrame()

        nrows = max(len(self.value),
                    len(self.class_.get_column_fields()) + 1)
        nrows += 1
        return pn.widgets.Tabulator(df,
                                     name="Data (Click to edit)",
                                     disabled=True,
                                     row_content=self._value_editor,
                                     sizing_mode='stretch_both',
                                     min_height=nrows*self.row_size,
                                     width_policy='max',
                                     height_policy='max',
                                     embed_content=False,
                                     show_index=False,
                                     
                                     )

    def make_newdoc_widget(self):
        model_editor = XeDocEditor(class_=self.class_, 
                                   allow_delete=False)
        def cb(event):
            if isinstance(event.new, self.class_):
                self.value.append(event.new)
                self.param.trigger('value')
            
        model_editor.param.watch(cb, 'value')

        return model_editor

    def _update_widgets(self, *events):
        self.table = self._make_table()
        self.newdoc = self.make_newdoc_widget()
        newdoc = pn.Card(self.newdoc, 
                    name='insert_new', 
                    header='➕', 
                    collapsed=True,
                    width_policy='max',
                    sizing_mode='stretch_width')
                    
        self._composite[:] = [newdoc, self.table]


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
    
    def __init__(self, **params):
        super().__init__(**params)
        self.param.watch(self._update_docs, ['class_', 'page', 'query', 'refresh_table'])

    def filter_callback(self, event):
        query = self.query_editor.value
        if self.query != query:
            self.query = query                
            self.page = 0
        if self.page == -1:
            self.page = 0
        end = math.ceil(self.class_.compile_query(**self.query).count()/self.page_size)
        self.param.page.bounds = (0, end)
        self.last_page = end
        self.refresh_table = True
        
    def trigger_refresh_cb(self, event):
        self.refresh_table = True
    
    def increment_page(self, event):
        self.page += 1

    def decrement_page(self, event):
        self.page -= 1

    def _set_docs(self, future):
        docs = future.result()
        with unlocked():
            self.docs = docs
            self.query_editor.loading = False

    def _get_page(self):
        skip = self.page*self.page_size
        docs = self.class_.find(**self.query, 
                                     _skip=skip, 
                                     _limit=self.page_size)
        return docs

    def _update_docs(self, *events):
        self.query_editor.loading = True
        loop = IOLoop.current()
        future = executor.submit(self._get_page)
        loop.add_future(future, self._set_docs)

    def value_editor(self, row):
        if len(self.docs)<=row.name:
            return pn.Column()

        doc = self.docs[row.name]

        columns = list(doc.get_column_fields())

        editor = XeDocEditor(value=doc,
                             class_=self.class_, 
                             fields=columns,
                             allow_delete=True,
                             show_debugger=False)

        editor.post_delete.append(self.trigger_refresh_cb)

        return pn.Column(editor)

    
    @pn.depends('refresh_table', 'docs')
    def table_panel(self):
        docs = [json_serializable(doc.index_labels) for doc in self.docs]
        df = pd.DataFrame(docs, columns=list(self.class_.get_index_fields()))

        table = pn.widgets.Tabulator(df,
                                     name="Data (Click to edit)",
                                     disabled=True,
                                     row_content=self.value_editor,
                                     sizing_mode='stretch_both', 
                                     embed_content=False,
                                     show_index=False,
                                     width=1000,
                                     min_height=500)
        return pn.Column( 
                         table, 
                         sizing_mode='stretch_width', 
                         width=1000, 
                         scroll=False,)

    @pn.depends('page','last_page')
    def page_controls(self):
        end = self.last_page or 1
        page_view = pn.indicators.LinearGauge(
            name='Page', value=self.page, bounds=(0, end), format='{value}',
            horizontal=True, width=75, min_height=75, align='end',
            tick_size='12px', title_size='12px', value_size='12px',
        )
       

        inc_page = pn.widgets.Button(name='\u25b6', disabled=(self.page >= self.last_page or self.page==-1),
                                    height=50, max_width=50, align='center', )
        inc_page.on_click(self.increment_page)

        dec_page = pn.widgets.Button(name='\u25c0', disabled=self.page<=0, align='center', 
                                    height=50, width=50, )
        dec_page.on_click(self.decrement_page)

        return pn.Row(dec_page, page_view,
                        inc_page , max_width=600, width_policy='max')


    @pn.depends('class_', 'query', 'page_size')
    def controls_panel(self):
        
        find_button = pn.widgets.Button(name='Query 🔍',
                                        button_type='primary', 
                                        align='center')
        find_button.on_click(self.filter_callback)

        self.query_editor = QueryEditor(class_=self.class_)
        
        self.model_editor = XeDocEditor(class_=self.class_, allow_delete=False)

        self.model_editor.post_save.append(self.trigger_refresh_cb)

        add_new = pn.Card(self.model_editor, 
                          name='insert_new', 
                          header='➕ New Document', 
                          collapsed=True)

        return pn.Column(
                        '##Filter documents \n(Valid JSON or python literals)',
                        self.query_editor,
                        find_button,
                        pn.layout.Divider(),
                        add_new,
                        )
    
    def __panel__(self):
        right_panel = pn.Column(self.page_controls, 
                                self.table_panel)
        left_panel = self.controls_panel
        return pn.Row(left_panel,
                      right_panel,
                      scroll=False,
                      width=1000, sizing_mode='stretch_width')

    
class XedocsEditor(pn.viewable.Viewer):
    _all_schemas = xedocs.schemas_by_category()

    controls_layout = param.ClassSelector(class_=ListPanel,
                                        is_instance=False,
                                        default=pn.Row)

    category = param.Selector(objects=list(_all_schemas))
    selected_schema = param.Selector(objects=[None])
    
    editor = param.ClassSelector(ModelTableEditor)
    
    def __init__(self, **params):
        schemas = params.pop('schemas', None)
        if schemas is not None:
            self._all_schemas = schemas
            self.param.category.objects = list(schemas)
        super().__init__(**params)


    @param.depends('category', watch=True, on_init=True)
    def category_changed(self):
        schemas = xedocs.schemas_by_category().get(self.category, {})

        if not schemas:
            return

        objects = list(schemas.values())
        self.param.selected_schema.names = schemas
        self.param.selected_schema.objects = objects
        self.selected_schema = objects[0]

    @pn.depends('controls_layout')
    def controls_panel(self):
        return self.controls_layout(self.param.category, self.param.selected_schema)

    @pn.depends('selected_schema')
    def model_panel(self):
        self.editor = ModelTableEditor(class_=self.selected_schema)
        return self.editor

    def __panel__(self):
        return pn.Column(self.controls_panel,
                        self.model_panel)

