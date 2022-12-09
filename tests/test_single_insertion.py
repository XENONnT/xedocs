#!/usr/bin/env python

from typing import List
import xedocs

from hypothesis import given, example, settings, assume
from hypothesis import strategies as st  # import integers, composite, SearchStrategy

from .functions_for_xedocs_test import save_test_data, check_insert_data
from .variables_for_test import *

import pytest


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.ElectronLifetime, value=floats))
def test_elife_data_insertion_into_straxen(docs: List[xedocs.schemas.ElectronLifetime]) -> None:

    collection = "electron_lifetimes"
    plugin = "corrected_areas"
    straxen_correction_name = 'elife'
    elife_col = db[collection]
    db.drop_collection(collection)

    saved_docs = save_test_data(docs, collection, db)

    check_insert_data(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)
   

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.ElectronDriftVelocity, value=floats))
def test_edrift_data_insertion_into_straxen(docs: List[xedocs.schemas.ElectronDriftVelocity]) -> None:
    collection = "electron_drift_velocities"
    plugin = "event_positions"
    straxen_correction_name = 'electron_drift_velocity'
    elife_col = db[collection]
    elife_col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_insert_data(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.DriftTimeGate, value=floats))
def test_e_drift_time_gate_insertion_into_straxen(docs: List[xedocs.schemas.DriftTimeGate]) -> None:
    collection = "electron_drift_time_gates"
    plugin = "event_positions"
    straxen_correction_name = 'electron_drift_time_gate'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)
 
    check_insert_data(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.RelativeLightYield, value=floats))
def test_rel_light_yield_data_insertion_into_straxen(docs: List[xedocs.schemas.RelativeLightYield]) -> None:
    collection = "relative_light_yield"
    plugin = "corrected_areas"
    straxen_correction_name = 'rel_light_yield'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_insert_data(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.BaselineSamplesNV, value=floats))
def test_baseline_sample_nv_insertion_into_straxen(docs: List[xedocs.schemas.BaselineSamplesNV]) -> None:
    collection = "baseline_samples_nv"
    plugin = "records_nv"
    straxen_correction_name = 'baseline_samples_nv'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_insert_data(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)


