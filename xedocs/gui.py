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

from panel.widgets import CompositeWidget

from pydantic_panel import (get_widget, 
                            json_serializable, 
                            PydanticModelEditor)

from .schemas import XeDoc


@get_widget.dispatch(precedence=1)
def get_widget(value: rframe.TimeInterval, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    end = getattr(field.field_info, 'lt', None)

    if isinstance(value, rframe.TimeInterval):
        value = value.left, value.right

    if isinstance(value, dict):
        value = value['left'], value['right']

    return pn.widgets.DatetimeRangePicker(value=value,
                                          start=start, end=end, **kwargs)

@get_widget.dispatch(precedence=1)
def get_widget(value: rframe.IntegerInterval, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    if start is not None:
        start += 1
    else:
        start = getattr(field.field_info, 'ge')

    end = getattr(field.field_info, 'lt', None)
    if end is not None:
        end -= 1
    else:
        end = getattr(field.field_info, 'le', None)

    if isinstance(value, rframe.IntegerInterval):
        value = value.left, value.right

    if isinstance(value, dict):
        value = value['left'], value['right']

    return pn.widgets.IntRangeSlider(value=value,
                                     start=start, end=end, **kwargs)


@json_serializable.dispatch(precedence=1)
def json_serializable(value: rframe.Interval):
    return (value.left, value.right)


class XeDocEditor(PydanticModelEditor):

    _trigger_recreate = ['class_', 'extra_widgets', 
                         'allow_save', 'allow_delete']

    datasource = param.Parameter(default=None)

    pre_save = param.HookList([])
    post_save = param.HookList([])
    pre_delete = param.HookList([])
    post_delete = param.HookList([])

    deleted = param.Boolean(False)

    allow_save = param.Boolean(True)

    allow_delete = param.Boolean(True)
    
    add_debugger = param.Boolean(True)
    
    def __init__(self, **params):
        if params.get('fields') is None:
            schema = params.get('class_') or params.get('value')
            index_fields = list(schema.get_index_fields())
            column_fields = list(schema.get_column_fields())
            params['fields'] = index_fields + column_fields

        super().__init__(**params)
        self.param.class_.class_ = XeDoc
        self.param.value.class_ = XeDoc
    
    def _update_save_button(self, target, event):
        target.disabled = event.new is None

    @property
    def can_delete(self):
        if self.deleted:
            return False
        try:
            self.value.pre_delete(self.datasource)
        except:
            return False
        return True
    
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


@get_widget.dispatch(precedence=1)
def get_widget(value: XeDoc, field: Any, **kwargs):
    return XeDocEditor(value=value, name=field.name, **kwargs)


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


class ModelTableEditor(pn.viewable.Viewer):
    class_ = param.ClassSelector(pydantic.BaseModel, is_instance=False)

    docs = param.List(class_=pydantic.BaseModel)
    

    query_editor = param.ClassSelector(QueryEditor)
    model_editor = param.ClassSelector(XeDocEditor)

    query = param.Dict({})

    page = param.Integer(0, bounds=(0, 1))
    page_size = param.Integer(15)
    
    refresh_table = param.Event()
    
    def __init__(self, **params):
        # params['query_editor'] = QueryEditor(model=params['model'], allow_query=False)
        super().__init__(**params)
        self.param.watch(self._update_docs, ['class_', 'page', 'query', 'refresh_table'])

    def filter_callback(self, event):
        query = self.query_editor.value
        if self.query != query:
            self.query = query                
            self.page = 0
        self.refresh_table = True
        
    def trigger_refresh_cb(self, event):
        self.refresh_table = True
    
    def increment_page(self, event):
        self.page += 1

    def decrement_page(self, event):
        self.page -= 1

    def _update_docs(self, *events):
        skip = self.page*self.page_size
        self.docs = self.class_.find(**self.query, 
                                     _skip=skip, 
                                     _limit=self.page_size)

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
                                     sizing_mode='stretch_both', width=1000,
                                     embed_content=False,
                                     show_index=False,
                                     min_height=500)
        return pn.Column(self.param.page, 
                    table, sizing_mode='stretch_width', width=1000, scroll=False,)
    
    @pn.depends('class_', 'query', 'page_size')
    def controls_panel(self):
        end = math.ceil(self.class_.compile_query(**self.query).count()/self.page_size)
        if not end:
            end = 1
        self.param.page.bounds = (0, end)

        inc_page = pn.widgets.Button(name='\u25b6', min_width=75, max_width=100, width_policy='auto')
        inc_page.on_click(self.increment_page)

        dec_page = pn.widgets.Button(name='\u25c0', min_width=75, max_width=100, width_policy='auto')
        dec_page.on_click(self.decrement_page)

        buttons = pn.Row(dec_page, inc_page, align='center', max_width=250)

        find_button = pn.widgets.Button(name='Query 🔍',
                                        button_type='primary', 
                                        align='center')
        find_button.on_click(self.filter_callback)

        self.query_editor = QueryEditor(class_=self.class_)
        
        self.model_editor = XeDocEditor(class_=self.class_, allow_delete=False)

        self.model_editor.post_save.append(self.trigger_refresh_cb)

        add_new = pn.Card(self.model_editor, 
                          name='insert_new', 
                          header='➕', 
                          collapsed=True)

        return pn.Column(
                        '##Filter documents \n(Valid JSON or python literals)',
                        self.query_editor,
                        find_button,
                        buttons,
                        pn.layout.Divider(),
                        add_new,
                        )
    
    def __panel__(self):
        return pn.Row(self.controls_panel,
                      self.table_panel,
                      scroll=False,
                      width=1000, sizing_mode='stretch_width')

    
class XedocsEditor(pn.viewable.Viewer):
    schema_name = param.Selector(objects=xedocs.list_schemas())
    
    editor = param.ClassSelector(ModelTableEditor)
    
    def __init__(self, **params):
        schemas = params.pop('schemas', xedocs.list_schemas())
        self.param.schema_name.objects = schemas
        self.schema_name = schemas[0]

        super().__init__(**params)
        
    def controls_panel(self):
        widget = pn.widgets.RadioButtonGroup(name='Schema', sizing_mode ='stretch_width',
                                             options= self.param.schema_name.objects,
                                             orientation='vertical')
        widget.link(self, value='schema_name')
        return pn.panel(widget)
    
    @pn.depends('schema_name')
    def model_panel(self):
        schema = xedocs.find_schema(self.schema_name)
        self.editor = ModelTableEditor(class_=schema)
        return self.editor

    def __panel__(self):
        return pn.Column(self.model_panel)

