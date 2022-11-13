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

Calibrations
------------

The calibration collections hold information about calibrations that were performed. 
All calibration schemas should inherit from ``xedocs.BaseCalibrationSchema`` or one of its subclasses.

The base schema includes a number of shared indices and fields. 
It also includes a validation method for the time field that allows you to set 
the time interval by passing the run_id field which will pull the time interval from the run database.

.. code-block:: python

    class BaseCalibation(XeDoc):
        """Base class for calibration metadata
        """

        class Config:
            allow_population_by_field_name = True

        time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex(alias='run_id')
        source: str = rframe.Index()

        operator: str
        comments: str

        @validator('time', pre=True)
        def run_id_to_time(cls, v):
            """Convert run id to time"""
            if isinstance(v, (str, int)):
                try:
                    v = settings.run_id_to_interval(v)
                except:
                    pass
            return v


Example: Utube calibrations


.. code-block:: python

    class UtubeCalibation(BaseCalibation):
        """Calibrations performed inside the utube
        """

        _ALIAS = "utube_calibrations"

        tube: Literal['top','bottom'] = rframe.Index()
        direction: Literal['cw','ccw'] = rframe.Index()

        depth_cm: float
