=======================================
XeDocs - XENON Metadata management tool
=======================================
xedocs is meant to replace cmt and bodega as well as helping tracking all shared documents especially if
they need to be versioned.

What does Xedocs give you
=========================

Data reading
------------

    - Read data from multiple formats (e.g. mongodb, pandas) and locations with a simple unified interface.
    - Custom logic implemented on the document class, e.g. creating a tensorflow model from the data etc.
    - Multiple APIs for reading data, fun functional, ODM style, pandas and xarray.
    - Read data as objects, dataframes, dicts, json.
    
Writing data
------------

    - Write data to multiple storage backends with the same interface
    - Custom per-collection rules for data insertion, deletion and updating.
    - Schema validation and type coercion so storage has uniform and consistent data.
    
Other
-----

    - Custom panel widgets for graphical representation of data, web client
    - Auto-generated API server and client + openapi documentation
    - CLI for viewing and downloading data


Basic Usage
-----------

Explore the available schemas

.. code-block:: python

    import xedocs

    >>> xedocs.list_schemas()
    >>> ['detector_numbers',
        'fax_configs',
        'plugin_lineages',
        'context_lineages',
        'pmt_gains',
        'global_versions',
        'electron_drift_velocities',
        ...]

    >>> xedocs.help('pmt_gains')

    >>>
            Schema name: pmt_gains
            Index fields: ['version', 'time', 'detector', 'pmt']
            Column fields: ['created_date', 'comments', 'value']
    

Read/write data from the staging database, this database is writable from the default analysis username/password

.. code-block:: python

    import xedocs

    db = xedocs.staging_db()

    docs = db.pmt_gains.find_docs(version='v1', pmt=[1,2,3,5], time='2021-01-01T00:00:00', detector='tpc')
    gains = [doc.value for doc in docs]

    doc = db.pmt_gains.find_one(version='v1', pmt=1, time='2021-01-01T00:00:00', detector='tpc')
    pmt1_gain = doc.value

Read from the shared production database, this database is read-only for the default analysis username/password


.. code-block:: python

    import xedocs

    db = xedocs.production_db()

    ...
    
You can also query documents directly from the schema class, 
Schemas will query the mongodb staging database by default, if no explicit datasource is given.

.. code-block:: python

    from xedocs.schemas import DetectorNumber

    drift_velocity = DetectorNumber.production_db.find_one(field='drift_velocity', version='v1')
    
    # Returns a Bodega object with attributes value, description etc.
    drift_velocity.value

    all_v1_documents = DetectorNumber.production_db.find(version='v1')



Read data from alternative data sources specified by path, 
e.g csv files which will be loaded by pandas.

.. code-block:: python

    from xedocs.schemas import DetectorNumber
    
    g1_doc = DetectorNumber.find_one(datasource='/path/to/file.csv', version='v1', field='g1')
    g1_value = g1_doc.value
    g1_error = g1_doc.uncertainty

The path can also be a github URL or any other URL supported by fsspec. 

.. code-block:: python

    from xedocs.schemas import DetectorNumber
    
    g1_doc = DetectorNumber.find_one(
                             datasource='github://org:repo@/path/to/file.csv', 
                             version='v1', 
                             field='g1')


Supported data sources

    - MongoDB collections
    - TinyDB tables
    - JSON files
    - REST API clients

Please open an issue on rframe_ if you want support for an additional data format.


Documentation
-------------
Full documentation hosted by Readthedocs_

Credits
-------


This package was created with Cookiecutter_ and the `briggySmalls/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage
.. _Readthedocs: https://xedocs.readthedocs.io/en/latest/
.. _rframe: https://github.com/jmosbacher/rframe