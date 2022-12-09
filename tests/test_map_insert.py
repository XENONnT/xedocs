from .functions_for_xedocs_test import * # check_map_correction
from .variables_for_test import *
import xedocs
import straxen
import unittest
import pytest


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s1_xyz_map_mlp_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.S1XYZMap, straxen_cor_name='s1_xyz_map',
                         xedocs_cor_name='s1_xyz_maps', output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_info',
                         algorithm='mlp', db_correction=xd_db.s1_xyz_maps)

    
@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s1_xyz_map_cnn_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.S1XYZMap, straxen_cor_name='s1_xyz_map',
                         xedocs_cor_name='s1_xyz_maps', output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_info',
                         algorithm='cnn', db_correction=xd_db.s1_xyz_maps)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s1_xyz_map_gcn_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.S1XYZMap, straxen_cor_name='s1_xyz_map',
                         xedocs_cor_name='s1_xyz_maps', output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_info',
                         algorithm='gcn', db_correction=xd_db.s1_xyz_maps)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s2_xy_map_mlp_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.S2XYMap, straxen_cor_name='s2_xy_map',
                         xedocs_cor_name='s2_xy_maps', output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_info',
                         algorithm='mlp', db_correction=xd_db.s2_xy_maps)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s2_xy_map_cnn_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.S2XYMap, straxen_cor_name='s2_xy_map',
                         xedocs_cor_name='s2_xy_maps',output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_info',
                         algorithm='cnn', db_correction=xd_db.s2_xy_maps)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s2_xy_map_gcn_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.S2XYMap, straxen_cor_name='s2_xy_map',
                         xedocs_cor_name='s2_xy_maps', output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_info',
                         algorithm='gcn', db_correction=xd_db.s2_xy_maps)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_fdc_map_mlp_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.FdcMap, straxen_cor_name='fdc_map',
                         xedocs_cor_name='fdc_maps',output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_positions',
                         algorithm='mlp', db_correction=xd_db.fdc_maps)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_fdc_map_cnn_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.FdcMap, straxen_cor_name='fdc_map',
                         xedocs_cor_name='fdc_maps',output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_positions',
                         algorithm='cnn', db_correction=xd_db.fdc_maps)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_fdc_map_gcn_into_straxen() -> None:
    xd_db = xedocs.staging_db()
    check_map_correction(schema=xedocs.schemas.FdcMap, straxen_cor_name='fdc_map',
                         xedocs_cor_name='fdc_maps',output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_positions',
                         algorithm='gcn', db_correction=xd_db.fdc_maps)

@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_s1_aft_xyz_into_straxen() -> None:

    xd_db = xedocs.staging_db()
    schema = xedocs.schemas.S1AFTXYZMap
    xedocs_cor_name = 's1_aft_xyz_maps'
    value = 's1_aft_dd_xyz_XENONnT_kr-83m_08Feb2022.json'
    straxen_cor_name = 's1_aft_map'

    check_map_correction(schema=schema, straxen_cor_name=straxen_cor_name,
                         xedocs_cor_name=xedocs_cor_name, output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_pattern_fit', value=value)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_bayes_model_mlp_into_straxen() -> None:

    st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
    xd_db = xedocs.staging_db()
    schema = xedocs.schemas.NaiveBayesClassifier
    xedocs_cor_name = 'bayes_models'
    straxen_cor_name = 'bayes_config_file'
    value = 'conditional_probabilities_and_bins_v1_w_global_v6.npz'

    check_map_correction(schema=schema, straxen_cor_name=straxen_cor_name,
                         xedocs_cor_name=xedocs_cor_name, output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_pattern_fit', value=value)


@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_posrec_mlp_into_straxen() -> None:

    st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
    xd_db = xedocs.staging_db()
    schema = xedocs.schemas.PosRecModel
    algorithm = 'mlp'
    xedocs_cor_name = 'posrec_models'
    value = 'xnt_mlp_wfsim_20201214.tar.gz'
    straxen_cor_name = 'tf_model_mlp'

    check_map_correction(schema=schema, straxen_cor_name=straxen_cor_name,
                         xedocs_cor_name=xedocs_cor_name, output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_pattern_fit', value=value,
                         algorithm=algorithm, db_correction=xd_db.posrec_models)



@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_posrec_cnn_into_straxen() -> None:
    st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
    xd_db = xedocs.staging_db()
    schema = xedocs.schemas.PosRecModel
    algorithm = 'cnn'
    xedocs_cor_name = 'posrec_models'
    value = 'xnt_cnn_wfsim_A_5_2000_20210112.tar.gz'
    straxen_cor_name = 'tf_model_cnn'

    check_map_correction(schema=schema, straxen_cor_name=straxen_cor_name,
                         xedocs_cor_name=xedocs_cor_name, output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_pattern_fit', value=value,
                         algorithm=algorithm, db_correction=xd_db.posrec_models)



@pytest.mark.skipif('straxen' not in installed, reason="Straxen is not installed skipping test")
@pytest.mark.skipif(not straxen.utilix_is_configured(), reason="No db access, cannot test!")
def test_posrec_gcn_into_straxen() -> None:
    st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
    xd_db = xedocs.staging_db()
    schema = xedocs.schemas.PosRecModel
    algorithm = 'cnn'
    xedocs_cor_name = 'posrec_models'
    value = 'xnt_gcn_wfsim_20201203.tar.gz'
    straxen_cor_name = 'tf_model_cnn'

    check_map_correction(schema=schema, straxen_cor_name=straxen_cor_name,
                         xedocs_cor_name=xedocs_cor_name, output_file=output_file,
                         run_id_nt=run_id_nt, db=db, plugin='event_pattern_fit', value=value,
                         algorithm=algorithm, db_correction=xd_db.posrec_models)




