Xedocs API Server
==========================

There is also an API server that can be used as a datasource for corrections.
To use it you will need an http client initializaed with the correction URL and an access token header.

.. code-block:: python

    import rframe
    import xedocs

    datasource = rframe.BaseHttpClient(URL,
                                       headers={"Authorization": "Bearer: TOKEN"})
    
    gain_docs = xedocs.PmtGains.find(datasource, pmt=1, version='v3')


to make things a bit easier, 
there is a utility function that will create an API client for you `xedocs.cmt_api_client`
If you dont have a token, it will attempt to use the xeauth package to get one for you (if installed).

You can install xeauth by running `pip install xeauth`

.. code-block:: python

    import xedocs

    datasource = xedocs.api_client('pmt_gains', readonly=True)
    # The script will attempt to open a browser for authentication
    # if the broswer does not open automatically, follow the link printed out.
    # Once you are authenticated as a xenon member, a readonly access token will be
    # retrieved automatically. If you change readonly to False, a token
    #with write permissions will be retrieved.


    gain_docs = xedocs.PmtGains.find(datasource, pmt=1, version='v3')


Inserting Corrections
---------------------

New correction documents can be inserted into a datasource with the `doc.save(datasource)` method.
Example:

.. code-block:: python

    import xedocs

    doc = xedocs.PmtGains(pmt=1, version='v3', value=1, ...)
    doc.save(datasource)

If all the conditions for insertion are met, e.g. the values for the given index not already being set, the insertion will be successful.

Of course you must have write access to the datasource for any insertion to succeed. The default datasources are all read-only.
When using the server to write values you must request a token with write permissions:

.. code-block:: python

    import xedocs

    # If you have to correction roles defined (correction expert), you can request a token with
    # extended scope i.e. write:all. This token will allow you to write to all correction collections
    # If you do not have the proper permissions, you will just get back the default token scope of read:all
    datasource = xedocs.api_client('pmt_gains', readonly=False)

    doc = xedocs.PmtGains(pmt=1, version='v3', value=1, ...)
    doc.save(datasource)

