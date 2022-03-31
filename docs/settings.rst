The settings object
===================
The xedocs.settings holds the global settings for the current python process.

Overriding default database
---------------------------

.. code-block:: python

    from xedocs import settings

    settings.DEFAULT_DATABASE = 'some_database'


Overriding default datasources
------------------------------
You can change which datasource is used by default (for the current session) for a given correction in the correction_settings:

.. code-block:: python

    from xedocs import settings

    settings.datasources['pmt_gains'] = MY_DEFAULT_DATASOURCE
