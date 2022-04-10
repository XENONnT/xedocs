Defining schemas
================

Xenon shared documents are defined using a schema that inherits from xedocs.XeDoc or one of its subclasses:

.. list-table:: Xedoc classes
    :widths: 25 25 50
    :header-rows: 1

    * - Class
      - Base classes
      - Used for
    * - XeDoc
      - rframe.BaseSchema
      - General documents/metadata.
    * - VersionedXeDoc
      - XeDoc
      - Versioned documents.
    * - BaseCorrectionSchema
      - VersionedXeDoc
      - Constant corrections.
    * - TimeSampledCorrection
      - BaseCorrectionSchema
      - Time dependent corrections where time dependence is sampled and linearly interpolated between samples.
    * - TimeIntervalCorrection
      - BaseCorrectionSchema
      - Time dependent corrections where time dependence is interval based.


Corrections
-----------

Correction definitions should subclass the ``xedocs.BaseCorrectionSchema`` or 
one of its subclasses and added via PR to xedocs so that they can be used in processing. 
When subclassing a Correction class, you must give it a unique ``name`` attibute.

``BaseCorrectionSchema`` subclasses:

    - TimeSampledCorrection - indexed by version and time, where time is a datetime
    - TimeIntervalCorrection - indexed by version and time, where time is a interval of datetimes

Any subclass of ``BaseCorrectionSchema`` will automatically become available in the ``xedocs.frames`` namespace

.. code-block:: python

    rdfs = xedocs.frames.pmt_gains

    # specific remote dataframes can be accessed via dict-like access or attribute access by their name
    rf = xedocs.frames.pmt_gains
    # or
    rf = xedocs.frames['pmt_gains']

    df = rf.sel(version=..., detector=..., time=...)


References
-----------

Some corrections are actually references, 
in this case there will be a .load() method to fetch the object being reference.

Examples:

.. code-block:: python

    # will return a reference to one or more correction documents
    ref = xedocs.CorrectionReference.find_one(correction='pmt_gains', version=..., time=...)

    # will fetch the corrections being references
    pmt_gains = ref.load()

    # will return a reference to a resource (a FDC map)
    ref = xedocs.FdcMapName.find_one(version=..., time=..., kind=...)

    # will return the map being referenced.
    fdc_map = ref.load()
