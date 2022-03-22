===========================================
XeDocs - AKA Corrections Managment Tool 2.0
===========================================

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


Read data from alternative data sources

.. code-block:: python

    import xedocs
    
    g1_doc = xedocs.find_one('bodega', datasource='/path/to/file.json', version='v1', field='g1')
    g1_value = g1_doc.value
    g1_error = g1_doc.uncertainty

The path can also be a github URL or any other URL supported by fsspec. 

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