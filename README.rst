=======================================
XeDocs - XENON Metadata management tool
=======================================

XeDocs manages tracking versioned detector numbers, replacing CMT and ideally all hard-coded values. 
XeDocs both looks up data from its own online database, and uses straxen URL-style lookup to find other resources. 
To upload data to the XeDocs database, you must submit it as a PR to https://github.com/XENONnT/corrections

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
        'pmt_area_to_pes',
        'global_versions',
        'electron_drift_velocities',
        ...]

    >>> xedocs.help('pmt_area_to_pes')

    >>>
            Schema name: pmt_area_to_pes
            Index fields: ['version', 'time', 'detector', 'pmt']
            Column fields: ['created_date', 'comments', 'value']
    

Read/write data from the shared development database, 
this database is writable from the default analysis username/password

.. code-block:: python

    import xedocs

    db = xedocs.development_db()

    docs = db.pmt_area_to_pes.find_docs(version='v1', pmt=[1,2,3,5], time='2021-01-01T00:00:00', detector='tpc')
    to_pes = [doc.value for doc in docs]
    
    # passing a run_id will attempt to fetch the center time of that run from the runs db
    doc = db.pmt_area_to_pes.find_one(version='v1', pmt=1, run_id=25000, detector='tpc')
    to_pe = doc.value

Read from the straxen processing database, this database is read-only for the default analysis username/password


.. code-block:: python

    import xedocs

    db = xedocs.straxen_db()

    ...

Read from the the corrections gitub repository, this database is read-only


.. code-block:: python

    import xedocs

    db = xedocs.corrections_repo(branch="master")

    ...

If you cloned the corrections gitub repo to a local folder, this database can be read too


.. code-block:: python

    import xedocs

    db = xedocs.local_folder(PATH_TO_REPO_FOLDER)

    ...


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

If you want a new datasource to be available from a schema class, you can register it to the class:

.. code-block:: python

    from xedocs.schemas import DetectorNumber
    
    DetectorNumber.register_datasource('github://org:repo@/path/to/file.csv', name='github_repo')

    # The source will now be available under the given name:

    g1_doc = DetectorNumber.github_repo.find_one(version='v1', field='g1')


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
