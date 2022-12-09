from .functions_for_xedocs_test * # import save_test_data, check_reprocessing
from .variables_for_test import *
import xedocs
import straxen
import unittest
import pytest


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.ElectronLifetime, value=floats))
def test_elife_data_reprocessing_straxen(docs: List[xedocs.schemas.ElectronLifetime]):
    collection = "electron_lifetimes"
    plugin = "corrected_areas"
    straxen_correction_name = 'elife'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_reprocessing(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.ElectronDriftVelocity, value=floats))
def test_e_drift_velocity_data_reprocessing_straxen(docs: List[xedocs.schemas.ElectronDriftVelocity]) -> None:
    collection = "electron_drift_velocities"
    plugin = "event_positions"
    straxen_correction_name = 'electron_drift_velocity'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_reprocessing(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.RelativeLightYield, value=floats))
def test_rel_light_yield_data_reprocessing_straxen(docs: List[xedocs.schemas.RelativeLightYield]) -> None:

    collection = "relative_light_yield"
    plugin = "corrected_areas"
    straxen_correction_name = 'rel_light_yield'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_reprocessing(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.DriftTimeGate, value=floats))
def test_e_drift_time_gate_reprocessing_straxen(docs: List[xedocs.schemas.DriftTimeGate]) -> None:
    # print(docs[0])
    collection = "electron_drift_time_gates"
    plugin = "event_positions"
    straxen_correction_name = 'electron_drift_time_gate'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_reprocessing(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.BaselineSamplesNV, value=floats))
def test_baseline_sample_nv_insertion_into_straxen(docs: List[xedocs.schemas.BaselineSamplesNV]) -> None:
    collection = "baseline_samples_nv"
    plugin = "records_nv"
    straxen_correction_name = 'baseline_samples_nv'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    # if some of the values are zero, try insertion expect division by 0 error
    # else treat it as any other value
    try:
        check_reprocessing(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)
    except ZeroDivisionError:
        assume(False)

