from functions_for_xedocs_test import save_test_data, check_cutax_insert_data
from variables_for_test import *
import xedocs
import straxen
import unittest
import pytest


@pytest.mark.skipif('cutax' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
@settings(deadline=None)
@given(time_sampled_correction_strategy(xedocs.schemas.ElectronDiffusionCte, value=floats))
def test_electron_diffusion_insert_cutax(docs: List[xedocs.schemas.ElectronDiffusionCte]):
    collection = "electron_diffusion_cte" #doble check this is the right name
    plugin = "cut_s2_width"
    straxen_correction_name = 'diffusion_constant'
    col = db[collection]
    col.drop()

    saved_docs = save_test_data(docs, collection, db)

    check_cutax_insert_data(saved_docs, collection, straxen_correction_name, plugin, output_file, run_id_nt)