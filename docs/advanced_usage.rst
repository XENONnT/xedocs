==============
Advanced Usage
==============

Schema definitions
------------------

To query data you need a schema, a python class that inherits from `rframe.BaseSchema`.
Lets say we want to store a collection of versioned documents 
indexed by the experiment, detector and version

.. code-block:: python
    import rframe
    from typing import Literal


    class ExampleSchema(rframe.BaseSchema):
        name = 'simple_dataframe'

        # The simplest index, matches on exact value. 
        # This is how we define a versioned document without 
        # time dependence
        experiment: Literal['1t', 'nt'] = rframe.Index()
        detector: Literal['tpc', 'nveto','muveto'] = rframe.Index()
        version: str = rframe.Index()

        # we can define as many fields as we like, each with its own type
        # defined using standard python annotations
        value: float
        error: float
        unit: str
        creator: str

    def pre_insert(self, db):
            # the base class implementation checks if any documents already exist at the index 
        # and raises an error if it does
            super().pre_insert(db)
            # here you can add any special logic to perform prior to inserts

    def pre_update(self, db, new):
            # the base class implementation raises an error if new values dont match
            # the current ones for this index. we allow replacing the current values
            # with identical ones because the current values may be inferred (i.e interpolated)
            # in which case we allow new documents with the interpolated values since that wont
            # change any interpolated values.
            super().pre_update(db, new)

            # add any extra logic/checks to perform here 


Database Queries
----------------

Once we have a schema, we can use it to query any of the supported data backends
This allows for a consistent interface to data stored in any backend.

.. code-block:: python

    import pymongo
    

    db = pymongo.MongoClient()['cmt2']['simple_dataframe']

    # or 
    db = pd.read_csv("pandas_dataframe.csv")

    docs = ExampleSchema.find(datasource=db, experiment=..., detector=..., version=...)

    # or
    doc = ExampleSchema.find_one(datasource=db, experiment=..., detector=..., version=...)


Inserting data
--------------
A schema can also help you insert new data into a data source, e.g. a mogodb collection.

.. code-block:: python

    import pymongo

    db = pymongo.MongoClient()['cmt2']['simple_dataframe']

    doc = ExampleSchema(experiment=..., detector=..., version=..., value=..., ...)

    doc.save(db) # this will insert the document into the collection

The details of how to insert data into are handled by the framework so that you can use
the same code independent of the data source.


The RemoteFrame
---------------

Alternatively we can use the ``RemoteFrame`` class to access/store documents in any supported backend.

.. code-block:: python

    rf = ExampleSchema.rframe(db)
    # or
    rf = rframe.RemoteFrame(ExampleSchema, db) 

**Reading specific rows**

Rows can be accessed by calling the dataframe with the rows index values, using pandas-like indexing ``df.loc[idx]``, ``df.at[idx, column]``, ``df[column].loc[idx]`` or with the xarray style ``df.sel(index_name=idx)`` method

.. code-block:: python

    # These methods will al return an identical pandas dataframe

    df = rf.loc[experiment,detector, version]
    
    df = rf.sel(experiment=experiment, detector=detector, version=version)
    
    df = rf.loc[experiment,detector, version]
    
    # Access a specific column to get a series back
    df = rf['value'].loc[experiment,detector, version]
    df = rf.value.loc[experiment,detector, version]

    # pandas-style scalar lookup returns a scalar
    value = rdf.at[(experiment,detector, version), 'value']
    # or call the dataframe with the column as argyment and index values as keyword arguments
    value = rf('value', experiment=experiment, detector=detector, version=version)

**Slicing**

You can also omit indices to get results back matching all values of the omitted index

.. code-block:: python

    df = rf.sel(version=version)

    # or
    df = rf.loc[experiment, detector, :]

    # or
    df = rf.loc[experiment]

    # or pass a list a values you want to match on:
    df = rf.sel(version=[0,1], experiment=experiment)

    # Slicing is also supported
    df = rf.sel(version=slice(2,10), detector=detector)


The interval index also supports passing a tuple/slice/begin,end keywords to query all intervals overlapping the given interval

.. code-block:: python

    df = rf.sel(version=version, time=(time1,time2))
    df = rf.loc[version, time1:time2]
    df = rf.get(version=version, begin=time1, end=time2)
