Xedocs API Server
==========================

There is also an API server that can be used as a datasource for corrections.
To use it you will need an http client initializaed with the correction URL and an access token header.

.. code-block:: python

    import xedocs

    db = xedocs.xedocs_api()
    
    df = db.posrec_models.find_df(version='v3', run_id=25000)


there is also a utility function that will create an API client for you `xedocs.get_api_client`
If you dont have a token, it will attempt to use the xeauth package to get one for you (if installed).

You can install xeauth by running `pip install xeauth`

.. code-block:: python

    import xedocs

    datasource = xedocs.get_api_client('pmt_gains')

    # The script will attempt to open a browser for authentication
    # if the broswer does not open automatically, follow the link printed out.
    gain_docs = xedocs.PmtGains.find(datasource, pmt=1, version='v3')


Inserting Corrections
---------------------

New correction documents can be inserted into a datasource with the `doc.save(datasource)` method.
Example:

.. code-block:: python

    import xedocs

    doc = xedocs.PmtAreaToPE(pmt=1, version='v3', value=1, ...)
    db.insert(doc)

If all the conditions for insertion are met, e.g. the values for the given index not already being set, the insertion will be successful.

Of course you must have write access to the datasource for any insertion to succeed.