from .functions_for_xedocs_test import save_test_data, check_reprocessing_dict
from .variables_for_test import *
import pytest


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.SingleElectronGain, value=floats, partition=st.just('ab')))
def test_segain_data_reprocessing_with_straxen(docs: List[xedocs.schemas.SingleElectronGain]) -> None:

    collection = "se_gains"
    plugin = "corrected_areas"
    straxen_correction_name = 'se_gain'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db, kind='dict')

    check_reprocessing_dict(saved_docs, straxen_correction_name, collection, plugin, output_file, run_id_nt)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.AvgSingleElectronGain, value=floats, partition=st.just('ab')))
def test_ave_segain_data_reprocessing_with_straxen(docs: List[xedocs.schemas.AvgSingleElectronGain]) -> None:

    collection = "avg_se_gains"
    plugin = "corrected_areas"
    straxen_correction_name = 'avg_se_gain'
    schema = xedocs.schemas.AvgSingleElectronGain
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db, kind = 'dict')

    check_reprocessing_dict(saved_docs, straxen_correction_name, collection, plugin, output_file, run_id_nt)

    
@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.RelExtractionEff, value=floats, partition=st.just('ab')))
def test_rel_extraction_eff_data_reprocessing_with_straxen(docs: List[xedocs.schemas.RelExtractionEff]) -> None:

    collection = "rel_extraction_effs"
    plugin = "corrected_areas"
    straxen_correction_name = 'rel_extraction_eff'
    schema = xedocs.schemas.RelExtractionEff
    col = db[collection]
    col.drop()


    saved_docs = save_test_data(docs, collection, db, kind = 'dict')

    check_reprocessing_dict(saved_docs, straxen_correction_name, collection, plugin, output_file, run_id_nt)


    
