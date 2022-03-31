The xedocs CLI
==============

The xedocs CLI can be used to view or download data in a terminal

Viewing data
------------

.. code-block:: bash

    xedocs find pmt_gains --detector=tpc --run_id=20000 --pmt=1,2,3

Downloading data
----------------

.. code-block:: bash

    xedocs download pmt_gains --path=. --detector=tpc --run_id=20000 --pmt=1,2,3



