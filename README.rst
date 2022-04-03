===========================================
XeDocs - AKA Corrections Managment Tool 2.0
===========================================
xedocs is meant to replace cmt and bodega as well as helping tracking all shared documents especially if
they need to be versioned.

Basic Usage
-----------

Explore the available schemas

.. code-block:: python

    import xedocs

    >>> xedocs.list_schemas()
    >>> ['bodega',
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
    

Read data from the default data source

.. code-block:: python

    import xedocs

    docs = xedocs.find('pmt_gains',  version='v1', pmt=[1,2,3,5], time='2021-01-01T00:00:00', detector='tpc')
    gains = [doc.value for doc in docs]

    doc = xedocs.find_one('pmt_gains',  version='v1', pmt=1, time='2021-01-01T00:00:00', detector='tpc')
    pmt1_gain = doc.value


You can also query documents directly from the scham class, 
Schemas will query the mongodb cmt2 database by default, if no explicit datasource is given.

.. code-block:: python
    
    drift_velocity = xedocs.Bodega.find_one(field='drift_velocity', version='v1')
    
    # Returns a Bodega object with attributes value, description etc.
    drift_velocity.value

    all_v1_documents = xedocs.Bodega.find(version='v1')



Read data from alternative data sources specified by path, 
e.g csv files which will be loaded by pandas.

.. code-block:: python

    import xedocs
    
    g1_doc = xedocs.find_one('bodega', datasource='/path/to/file.csv', version='v1', field='g1')
    g1_value = g1_doc.value
    g1_error = g1_doc.uncertainty

The path can also be a github URL or any other URL supported by fsspec. 

.. code-block:: python

    import xedocs
    
    g1_doc = xedocs.find_one('bodega',
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