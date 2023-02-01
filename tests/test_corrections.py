import time
import datetime
import numbers
import os
from typing_extensions import dataclass_transform
import unittest
from typing import List

import pandas as pd
import pydantic
import pymongo
import pytz
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from rframe.schema import InsertionError, UpdateError
from xedocs.schemas import (
    BaseCorrectionSchema,
    TimeSampledCorrection,
    TimeIntervalCorrection,
)
import xedocs


def round_datetime(dt):
    return dt.replace(microsecond=int(dt.microsecond / 1000) * 1000, second=0)


# enforce datetimes are in the a reasonable range
# pandas nanosecond resolution has trouble with extreme dates
datetimes = st.datetimes(
    min_value=datetime.datetime(2000, 1, 1, 0, 0),
    max_value=datetime.datetime(2231, 1, 1, 0, 0),
).map(round_datetime)
floats = st.floats(
    min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False
)


def mongo_uri_not_set():
    return "TEST_MONGO_URI" not in os.environ


def api_server_not_set():
    return "TEST_CMT_SERVER_URI" not in os.environ


def make_datetime_index(start, stop, step="1d"):
    if isinstance(start, numbers.Number):
        start = pd.to_datetime(
            start,
            unit="s",
        )
    if isinstance(stop, numbers.Number):
        stop = pd.to_datetime(stop, unit="s")
    return pd.date_range(start, stop, freq=step)


def make_datetime_interval_index(start, stop, step="1d"):
    if isinstance(start, numbers.Number):
        start = pd.to_datetime(start, unit="s")
    if isinstance(stop, numbers.Number):
        stop = pd.to_datetime(stop, unit="s")
    return pd.interval_range(start, stop, periods=step)


@st.composite
def non_overlapping_interval_lists(draw, elements=st.datetimes(), min_size=2):
    elem = draw(st.lists(elements, unique=True, min_size=min_size * 2).map(sorted))
    return list(zip(elem[:-1:2], elem[1::2]))


@st.composite
def non_overlapping_interval_ranges(draw, elements=st.datetimes(), min_size=2):
    elem = draw(st.lists(elements, unique=True, min_size=min_size).map(sorted))
    return list(zip(elem[:-1], elem[1:]))


def pmt_to_pe_space(datetime_range=datetime.timedelta(days=100)):
    utcnow = datetime.datetime.utcnow()
    data = dict(
        version=["ONLINE"] + ["v{i}" for i in range(10)],
        detector=["tpc", "neutron_veto", "muon_veto"],
        pmt=list(range(100)),
        time=make_datetime_index(utcnow - datetime_range, utcnow + datetime_range),
    )


class SimpleCorrection(BaseCorrectionSchema):
    _ALIAS = "simple_correction"

    value: float


class SomeSampledCorrection(TimeSampledCorrection):
    _ALIAS = "sampled_correction"

    value: float


class SomeTimeIntervalCorrection(TimeIntervalCorrection):
    _ALIAS = "time_interval_correction"

    value: float


@st.composite
def time_interval_corrections_strategy(draw, **overrides):
    docs = draw(
        st.lists(
            st.builds(
                SomeTimeIntervalCorrection,
                time=datetimes,
                created_date=datetimes,
                **overrides,
            ),
            min_size=1,
            unique_by=lambda x: (x.version, x.time.left),
        )
    )

    last = docs[-1].time.left + datetime.timedelta(days=10)
    times = sorted([doc.time.left for doc in docs]) + [last]

    for doc, left, right in zip(docs, times[:-1], times[1:]):
        # very small differences may be hard to test for correctness
        assume((right - left) > datetime.timedelta(seconds=10))

        doc.time = left, right

    return docs


class TestCorrections(unittest.TestCase):
    """
    Requires write access to some pymongo server, the URI of witch is to be set
    as an environment variable under:

        TEST_MONGO_URI

    """

    _run_test = True

    def setUp(self):
        # Just to make sure we are running some mongo server, see test-class docstring
        if "TEST_MONGO_URI" not in os.environ:
            self._run_test = False
            return
        uri = os.environ.get("TEST_MONGO_URI")
        db_name = "test_cmt2"
        db = pymongo.MongoClient(uri)[db_name]

        self.collections = {name: db[name] for name in xedocs.list_schemas()}
        for collection in self.collections.values():
            collection.drop()

    @unittest.skipIf(mongo_uri_not_set(), "No access to test database")
    def tearDown(self):
        for collection in self.collections.values():
            collection.drop()

    @unittest.skipIf(mongo_uri_not_set(), "No access to test database")
    @given(
        st.lists(
            st.builds(SomeSampledCorrection, version=st.just("v1"), value=floats),
            min_size=3,
            unique_by=lambda x: x.time,
        )
    )
    @settings(deadline=None)
    def test_sampled_correction_v1(self, docs: List[SomeSampledCorrection]):
        name = SomeSampledCorrection._ALIAS
        datasource = self.collections[name]
        datasource.delete_many({})

        # we must sort by time before inserting

        docs = sorted(docs, key=lambda x: x.time)

        for doc1, doc2 in zip(docs[:-1], docs[1:]):
            # Require minimum 10 second spacing between samples
            # otherwise we get into trouble with rounding
            assume((doc2.time - doc1.time) > datetime.timedelta(seconds=10))

        # since values are interpolated in time
        prev = 0.0
        for doc in docs:
            if abs(doc.value - prev) < 1:
                doc.value += 2
            prev = doc.value
            doc.save(datasource)

        df_original = pd.DataFrame([doc.pandas_dict() for doc in docs]).set_index(
            ["version", "time"]
        )

        for doc1, doc2 in zip(docs[:-1], docs[1:]):
            dt = doc1.time + (doc2.time - doc1.time) / 2

            doc_interp = SomeSampledCorrection.find_one(datasource, time=dt)

            assert (
                doc_interp is not None
            ), f"No interpolated value found for date {dt} in {list(datasource.find())}"

            half_value = (doc2.value + doc1.value) / 2

            # avoid any division by small numbers
            if abs(doc_interp.value) < 1e-9:
                continue

            error = abs(half_value - doc_interp.value) / abs(doc2.value - doc1.value)

            self.assertAlmostEqual(error, 0, delta=1e-2)

            new_doc = SomeSampledCorrection(
                version="v1",
                time=dt,
                value=2 * (half_value + 10),
                created_date=doc_interp.created_date,
            )

            # changing values is not allowed
            with self.assertRaises(UpdateError):
                new_doc.save(datasource)

            # saving the same value as existing document should be allowed
            new_doc.value = doc_interp.value
            new_doc.save(datasource)

    @unittest.skipIf(mongo_uri_not_set(), "No access to test database")
    @given(
        st.lists(
            st.builds(
                SomeSampledCorrection,
                version=st.just("ONLINE"),
                run_id=datetimes,
                value=floats,
            ),
            min_size=3,
            unique_by=lambda x: str(x.time),
        )
    )
    @settings(deadline=None)
    def test_sampled_correction_online(self, docs: List[SomeSampledCorrection]):
        name = SomeSampledCorrection._ALIAS
        datasource = self.collections[name]
        datasource.delete_many({})

        # we must sort by time before inserting
        # since values are interpolated in time
        docs = sorted(docs, key=lambda x: x.time)

        for doc in docs:
            clock = xedocs.settings.clock

            if clock.after_cutoff(doc.time, buffer=2):
                doc.save(datasource)

            # If the time is before the cutoff, should raise an error
            elif not clock.after_cutoff(doc.time):
                current = SomeSampledCorrection.find_one(datasource, **doc.index_labels)
                if current and current.same_values(doc):
                    doc.save(datasource)
                else:
                    error = UpdateError if current else InsertionError
                    with self.assertRaises(error):

                        doc.save(datasource)
                    # insert data manually for testing
                    datasource.insert_one(doc.dict())
                if not clock.after_cutoff(doc.time, buffer=-5):
                    now = clock.current_datetime()
                    found = SomeSampledCorrection.find(datasource, time=now)
                    self.assertLessEqual(1, len(found))

    @unittest.skipIf(mongo_uri_not_set(), "No access to test database")
    @given(time_interval_corrections_strategy(version=st.just("v1"), value=floats))
    @settings(deadline=None)
    def test_interval_correction_v1(self, docs: List[SomeTimeIntervalCorrection]):
        name = SomeTimeIntervalCorrection._ALIAS
        datasource = self.collections[name]
        datasource.delete_many({})

        clock = xedocs.settings.clock

        for doc in docs:
            doc.save(datasource)

            dt = doc.time.left + (doc.time.right - doc.time.left) / 2
            doc_found = SomeTimeIntervalCorrection.find_one(datasource, time=dt)
            self.assertEqual(doc.value, doc_found.value)

        for doc in docs[:-1]:
            dt = doc.time.left + (doc.time.right - doc.time.left) / 2
            doc_found = SomeTimeIntervalCorrection.find_one(datasource, time=dt)
            self.assertEqual(doc.value, doc_found.value)

            doc_found.value += 1
            if clock.after_cutoff(doc.time.left):
                doc_found.save(datasource)
            else:
                with self.assertRaises(UpdateError):
                    doc_found.value = 2 * doc_found.value + 1
                    doc_found.save(datasource)
            doc.save(datasource)

        last_doc = docs[-1]
        left, right = last_doc.time.left, last_doc.time.right

        if not clock.after_cutoff(left) and clock.after_cutoff(right):
            cutoff = clock.cutoff_datetime()
            half_diff = (cutoff - left) / 2
            if half_diff > datetime.timedelta(seconds=1):
                with self.assertRaises(UpdateError):
                    last_doc.time = (left, left + half_diff)
                    last_doc.save(datasource)
        else:
            last_doc.time = left, right + datetime.timedelta(days=1)
            last_doc.save(datasource)
