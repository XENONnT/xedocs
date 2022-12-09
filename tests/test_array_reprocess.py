from functions_for_xedocs_test import check_reprocessing_array, create_array_docs
from variables_for_test import *
import numpy as np
import pytest

"""
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
def test_pmt_correction_reprocessing_into_straxen() -> None:

    collection = "hit_thresholds"
    plugin = "lone_hits"
    straxen_correction_name = 'hit_min_amplitude'
    detector = 'tpc'
    num_of_sensors = straxen.n_tpc_pmts
    schema = xedocs.schemas.HitThreshold
    col = db[collection]
    col.drop()

    create_array_docs(pmt_data, num_of_sensors, schema, detector, db, collection)

    saved_docs = schema.find(version = "v*", datasource = db[collection], detector = detector)

    check_reprocessing_array(saved_docs, schema, detector, straxen_correction_name, collection, plugin, output_file, run_id_nt)

"""
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
def test_nveto_correction_reprocessing_into_straxen() -> None:

    collection = "hit_thresholds"
    plugin = "records_nv"
    straxen_correction_name = 'hit_min_amplitude_nv'
    detector = 'neutron_veto'
    num_of_sensors = straxen.n_nveto_pmts
    schema = xedocs.schemas.HitThreshold
    col = db[collection]
    col.drop()

    create_array_docs(nveto_data, num_of_sensors, schema, detector, db, collection)

    saved_docs = schema.find(version = "v*", datasource = db[collection], detector = detector)

    check_reprocessing_array(saved_docs, schema, detector, straxen_correction_name, collection, plugin, output_file, run_id_nt)
    
"""
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
def test_mveto_correction_insertion_into_straxen() -> None:

    collection = "hit_thresholds"
    plugin = "hitlets_mv"
    straxen_correction_name = 'hit_min_amplitude_mv'
    detector = 'muon_veto'
    num_of_sensors = straxen.n_mveto_pmts
    schema = xedocs.schemas.HitThreshold
    col = db[collection]
    col.drop()

    create_array_docs(mveto_data, num_of_sensors, schema, detector, db, collection)

    saved_docs = schema.find(version="v*", datasource=db[collection], detector=detector)

    check_reprocessing_array(saved_docs, detector, straxen_correction_name, collection, plugin, output_file, run_id_nt)
"""
