import math
import param
import rframe
import xedocs
import datetime
import pydantic

import numpy as np
import pandas as pd
import panel as pn
from typing import Dict, List, Any, Literal, _LiteralGenericAlias
from pydantic import ValidationError, BaseModel
from functools import singledispatch, _find_impl
from plum import dispatch, NotFoundLookupError
from numbers import Integral, Number, Rational

ListInput = type('ListInput', (pn.widgets.LiteralInput, ), {'type': list})
DictInput = type('DictInput', (pn.widgets.LiteralInput, ), {'type': dict})
TupleInput = type('TupleInput', (pn.widgets.LiteralInput, ), {'type': tuple})


@dispatch
def get_widget(value: Integral, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    end = getattr(field.field_info, 'lt', None)
    return pn.widgets.IntInput(value=value, start=start,
                               end=end, **kwargs)

@dispatch
def get_widget(value: Number, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    end = getattr(field.field_info, 'lt', None)
    return pn.widgets.NumberInput(value=value, start=start,
                                  end=end, **kwargs)

@dispatch
def get_widget(value: bool, field: Any, **kwargs):
    if value is None:
        value = False
    return pn.widgets.Checkbox(value=value, **kwargs)

@dispatch
def get_widget(value: str, field: Any, **kwargs):
    max_len = field.field_info.max_length
    if max_len is not None and max_len < 100:
        return pn.widgets.TextInput(value=value, **kwargs)
    return pn.widgets.input.TextAreaInput(value=value, **kwargs)

@dispatch
def get_widget(value: List, field: Any, **kwargs):
    return ListInput(value=value, **kwargs)

@dispatch
def get_widget(value: Dict, field: Any, **kwargs):
    return DictInput(value=value, **kwargs)

@dispatch
def get_widget(value: tuple, field: Any, **kwargs):
    return TupleInput(value=value, **kwargs)

@dispatch
def get_widget(value: np.ndarray, field: Any, **kwargs):
    return pn.widgets.ArrayInput(value=value, **kwargs)

@dispatch
def get_widget(value: datetime.datetime, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    end = getattr(field.field_info, 'lt', None)
    return pn.widgets.DatetimePicker(value=value, start=start, end=end, **kwargs)

@dispatch
def get_widget(value: rframe.TimeInterval, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    end = getattr(field.field_info, 'lt', None)
    return pn.widgets.DatetimeRangePicker(value=value,
                                          start=start, end=end, **kwargs)

@dispatch
def get_widget(value: rframe.IntegerInterval, field: Any, **kwargs):
    start = getattr(field.field_info, 'gt', None)
    end = getattr(field.field_info, 'lt', None)
    return pn.widgets.IntRangeSlider(value=value,
                                     start=start, end=end, **kwargs)

@dispatch
def get_widget(value: Any, field: Any, **kwargs):
    if type(field.outer_type_) == _LiteralGenericAlias:
        options = list(field.outer_type_.__args__)
        if value not in options:
            values = options[0]
        return pn.widgets.Select(value=value, options=options,
                                 **kwargs)
    return pn.widgets.LiteralInput(value=value, **kwargs)


def pydantic_editor(model, hidden=(), widget_kwargs={}):
    widgets = {}
    
    def validate(event):
        if not event:
            return
        data = {k: widgets[k].value for k in widgets}
        try:
            model.validate(data)
            for k,v in data.items():
                setattr(model, k, v)
        except:
            if event:
                event.obj.value = event.old
            raise ValueError("Failed pydantic validation")

    for name, field in model.__fields__.items():
        
        value = getattr(model, name, None)
        try:
            widget = get_widget.invoke(field.outer_type_, field.__class__)(value, field, **widget_kwargs)
        except (NotFoundLookupError, NotImplementedError):
            widget = get_widget(value, field, **widget_kwargs)
        widget.param.watch(validate, 'value')
        widgets[name] = widget
    return pn.Column(*[w for name, w in widgets.items() if name not in hidden])


@dispatch
def json_serializable(value: pd.Interval):
    return (value.left, value.right)

@dispatch
def json_serializable(value: rframe.Interval):
    return (value.left, value.right)


@dispatch
def json_serializable(value: list):
    return [json_serializable(v) for v in value]

@dispatch
def json_serializable(value: tuple):
    return tuple(json_serializable(v) for v in value)

@dispatch
def json_serializable(value: dict):
    return {json_serializable(k): json_serializable(v) for k,v in value.items()}

@dispatch
def json_serializable(value: Any):
    return value


class pydantic_widgets(param.ParameterizedFunction):
    model = param.ClassSelector(pydantic.BaseModel, is_instance=False)
    
    aliases = param.Dict({})
    
    widget_kwargs = param.Dict({})
    defaults = param.Dict({})
    use_model_aliases = param.Boolean(False)
    callback = param.Callable(default=None)
    
    def __call__(self, **params):
        p = param.ParamOverrides(self, params)
        
        if p.use_model_aliases:
            default_aliases = {field.name: field.alias.capitalize() for name in p.model.__fields__.values()}
        else:
            default_aliases = {name: name.replace('_', ' ').capitalize() for name in p.model.__fields__}
        
        aliases = params.get('aliases', default_aliases)
        
        widgets = {}
        for field_name, alias  in aliases.items():
            field = p.model.__fields__[field_name]
            
            value = p.defaults.get(field_name, None)
            if value is None:
                value = field.default
            value = json_serializable(value)
            try:
                widget = get_widget.invoke(field.outer_type_, field.__class__)(value, field, name=alias, **p.widget_kwargs)
            except (NotFoundLookupError, NotImplementedError):
                widget = get_widget(value, field, name=alias, **p.widget_kwargs)
            if p.callback is not None:
                widget.param.watch(p.callback, 'value')
            widgets[field_name] = widget
        return widgets
    

class ModelEditor(param.Parameterized):
    model = param.ClassSelector(pydantic.BaseModel, is_instance=False)
    datasource = param.Parameter(default=None)
    pre_save = param.HookList()
    post_save = param.HookList()
    pre_delete = param.HookList()
    post_delete = param.HookList()
    deleted = param.Boolean(False)
    busy = param.Boolean(False)
    aliases = param.Dict()
    
    _widgets = param.Dict()
    
    def __init__(self, use_model_aliases=False, **params): 
        model = params['model']
        defaults = params.pop('defaults', {})
        
        if isinstance(model, pydantic.BaseModel):
            for name in model.__fields__:
                val = getattr(model, name)
                defaults[name] = json_serializable(val)
            params['model'] = model.__class__
            
        fields = list(model.get_index_fields()) + list(model.get_column_fields())
        
        if use_model_aliases:
            default_aliases = {name: fields[name].alias.capitalize() for name in fields}
        else:
            default_aliases = {name: name.replace('_', ' ').capitalize() for name in fields}
        
        params['aliases'] = params.get('aliases', default_aliases)
        
        super().__init__(**params)
        self._widgets = pydantic_widgets(defaults=defaults,
                                         callback=self._validate, **params)
    
    @property
    def data(self):
        return {k: v.value for k,v in self._widgets.items()}
    
    @property
    def value(self):
        return self.model(**self.data)
    
    @property
    def can_delete(self):
        try:
            self.value.pre_delete(self.datasource)
        except:
            return False
        return True
    
    def alias_to_field(self, alias):
        for field, field_alias in self.aliases.items():
            if alias == field_alias:
                return field
    
    def _validate(self, event):
        if not event:
            return
        name = event.obj.name
        field_name = self.alias_to_field(name)
        field = self.model.__fields__[field_name]
        data = self.data
        val = data.pop(field_name, None)
        val, error = field.validate(val, data, loc=name)
        if error:
            event.obj.value = event.old
            raise ValidationError([error])

    def _save_clicked(self, event):
        event.obj.name = 'Saving...'
        event.obj.panel.loading = True
        
        try:
            doc = self.value
            for cb in self.pre_save:
                cb(doc)    
            
            doc.save(self.datasource)
            
            for cb in self.post_save:
                cb(doc)
        finally:
            event.obj.name = 'Save'
            event.obj.panel.loading = False
        
    def _delete_clicked(self, event):
        if event.obj.name == 'Delete':
            event.obj.name = 'Confirm?'
            return
        
        event.obj.name = 'Deleting...'
        event.obj.panel.loading = True
        try:
            doc = self.value
            
            for cb in self.pre_delete:
                cb(doc)
                
            doc.delete(self.datasource)
            self.deleted = True
            
            for cb in self.post_delete:
                cb(doc)
        finally:
            event.obj.name = 'Deleted.'
            event.obj.panel.loading = False
        
    def panel(self, names=None, allow_save=True, allow_delete=True):
        if names is None:
            names = list(self._widgets)
        widgets = pn.Column(*[self._widgets[name] for name in names])
        
        if allow_save:
            save_button = pn.widgets.Button(name='Save 💾', button_type='success')
            save_button.on_click(self._save_clicked)
            save_button.panel = widgets
            widgets.append(save_button)
            
        if allow_delete and self.can_delete:
            delete_button = pn.widgets.Button(name='Delete 🗑️', button_type='danger')
            delete_button.on_click(self._delete_clicked)
            delete_button.panel = widgets
            widgets.append(delete_button)
            
        # panel = pn.Column(*widgets, sizing_mode='stretch_height', loading_indicator=True)
        return widgets

class QueryEditor(param.Parameterized):
    model = param.ClassSelector(pydantic.BaseModel, is_instance=False)
    datasource = param.Parameter(default=None)
    
    aliases = param.Dict()
    
    widget_kwargs = param.Dict({})
    
    _widgets = param.Dict()
    
    docs = param.List(class_=pydantic.BaseModel)
    
    def __init__(self, use_model_aliases=False, **params):
        model = params['model']
        defaults = params.pop('defaults', {})
        
        if isinstance(params['model'], pydantic.BaseModel):
            for name in params['model'].__fields__:
                val = getattr(params['model'], name)
                defaults[name] = json_serializable(val)
                
        fields = model.get_index_fields()
        
        if use_model_aliases:
            default_aliases = {name: fields[name].alias.capitalize() for name in fields}
        else:
            default_aliases = {name: name.replace('_', ' ').capitalize() for name in fields}
        
        params['aliases'] = params.get('aliases', default_aliases)
        
        super().__init__(**params)
        
        self._make_widgets(**defaults)
    
    @property
    def query(self):
        return {k: v.value for k,v in self._widgets.items()}
    
    def _make_widgets(self, **defaults):
        widgets = {}
        for field_name, alias  in self.aliases.items():
            field = self.model.__fields__[field_name]
            
            value = defaults.get(field_name, None)
            if value is None:
                value = field.default
            value = json_serializable(value)
            widgets[field_name] = pn.widgets.LiteralInput(value=value, name=alias, **self.widget_kwargs)
        self._widgets = widgets
    
    def _find_clicked(self, event):
        self.docs = self.model.find(self.datasource, **self.query)
        
    def panel(self, names=None, allow_query=True):
        if names is None:
            names = list(self._widgets)
        widgets = [self._widgets[name] for name in names]
        if allow_query:
            query_button = pn.widgets.Button(name='🔍 Find', button_type='success')
            query_button.on_click(self._find_clicked)
            widgets.append(query_button)
        return pn.Column(*widgets)
        
        
class ModelTableEditor(param.Parameterized):
    model = param.ClassSelector(pydantic.BaseModel, is_instance=False)
    docs = param.List(class_=pydantic.BaseModel)
    
    query_editor = param.ClassSelector(QueryEditor)
    model_editor = param.ClassSelector(ModelEditor)
    query = param.Dict({})
    page = param.Integer(0, bounds=(0, 1))
    page_size = param.Integer(15)
    
    refresh_table = param.Event()
    
    def __init__(self, **params):
        params['query_editor'] = QueryEditor(model=params['model'])
        super().__init__(**params)
    
    def filter_callback(self, event):
        if self.query != self.query_editor.query:
            self.query = self.query_editor.query                
            self.page = 0
        self.refresh_table = True
        
    def trigger_refresh_cb(self, event):
        self.refresh_table = True
    
    def increment_page(self, event):
        self.page += 1

    def decrement_page(self, event):
        self.page -= 1

    def value_editor(self, row):

        if len(self.docs)<=row.name:
            return pn.Column()
        
        doc = self.docs[row.name]
        
        columns = list(doc.get_column_fields())
        editor = ModelEditor(model=doc)
        editor.post_delete.append(self.trigger_refresh_cb)
        return editor.panel(names=columns, allow_delete=True)
        
    @pn.depends('page', 'refresh_table')
    def table_panel(self):
        if self.page<0:
            self.page = 0
        skip = self.page*self.page_size
        self.docs = self.model.find(**self.query, _skip=skip, _limit=self.page_size)
        docs = [json_serializable(doc.index_labels) for doc in self.docs]
        # docs.append({k: None for k in self.model.get_index_fields()})
        df = pd.DataFrame(docs)
        
        table = pn.widgets.Tabulator(df,
                                     name="Data (Click to edit)",
                                     disabled=True,
                                     row_content=self.value_editor,
                                     sizing_mode='stretch_width', width=1000,
                                     embed_content=False,
                                     show_index=False, height=1200)

        return pn.Column(self.param.page, 
                    table, sizing_mode='stretch_width', height=1200, width=1000, scroll=False,)
    
    @pn.depends('query')
    def controls_panel(self):
        end = math.ceil(self.model.compile_query(**self.query).count()/self.page_size)
        if not end:
            end = 1
        self.param.page.bounds = (0, end)

        inc_page = pn.widgets.Button(name='\u25b6', min_width=75, max_width=100, width_policy='auto')
        inc_page.on_click(self.increment_page)

        dec_page = pn.widgets.Button(name='\u25c0', min_width=75, max_width=100, width_policy='auto')
        dec_page.on_click(self.decrement_page)

        buttons = pn.Row(dec_page, inc_page, align='center', max_width=250)

        find_button = pn.widgets.Button(name='Apply Filter 🔍', button_type='primary', align='center')
        find_button.on_click(self.filter_callback)

        columns = list(self.model.get_index_fields()) + list(self.model.get_column_fields())
        editor = ModelEditor(model=self.model)
        editor.post_save.append(self.trigger_refresh_cb)
        
        return pn.Column(
                        '##Filter documents \n(Valid JSON or python literals)',
                        self.query_editor.panel(allow_query=False),
                        find_button,
                        buttons,
                        pn.layout.Divider(),
                        '##New document', 
                        editor.panel(names=columns, allow_delete=False),
                        )
    
    def panel(self, allow_insert=False):
       
        return pn.Row(self.controls_panel,
                      self.table_panel,
                      scroll=False,
                      width=1000, sizing_mode='stretch_width')

    
class XedocsEditor(param.Parameterized):
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
        self.editor = ModelTableEditor(model=schema)
        return self.editor.panel()

    def panel(self):
        return pn.Column(self.controls_panel(), self.model_panel,)

