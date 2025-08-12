import xedocs
import unittest
import time
import datetime
import pytest
from typing import List
import pkg_resources
import pytest
from importlib import import_module
import pymongo
import os
import strax
import numpy as np

from hypothesis import given, example, settings, assume
from hypothesis import strategies as st  # import integers, composite, SearchStrategy

# This can be replaced with any output file just needed to put it here to work in dali 
output_file = '/dali/lgrandi/lsanchez3/scratch-midway2/strax_data'

def round_datetime(dt):
    return dt.replace(microsecond=int(dt.microsecond / 1000) * 1000, second=0)

######### Sources to sample data from ##########

datetimes = st.datetimes(
    min_value=datetime.datetime(2000, 1, 1, 0, 0),
    max_value=datetime.datetime(2231, 1, 1, 0, 0)).map(round_datetime)

run_ids = st.integers(
    min_value=1,
    max_value=999999)
floats = st.floats(
    min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False
)

######### Run id for testing data #############

run_id_nt = '047493'

# Checks if straxen is in your library
required = {"straxen"}  # list of required libraries
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed


###### Builds data to use in the corrections #########3
def time_sampled_correction_strategy(correction, **overrides):
    docs = st.lists(
        st.builds(correction,
                  version=st.just("v*"),
                  run_id=datetimes,
                  **overrides),
        min_size=3,
        max_size=5,
        unique_by=lambda x: x.time
    )

    return docs

def dict_correction_strategy(correction, **overrides):
    docs = st.lists(
        st.builds(correction,
                  version=st.just("v*"),
                  partition=st.just('ab'), #this might be completly unnecesarry due to the ovverrides
                  run_id=datetimes,
                  **overrides),
        min_size=3,
        max_size=5,
        unique_by=lambda x: x.time
    )

    return docs

# import straxen only if you have it
if len(missing) == 0:
    import straxen



@unittest.skipIf(len(missing) != 0, "Skip this test if straxen is not installed")  # checks if straxen is installed
class TestStraxenDateWithXedocsCorrections(unittest.TestCase):
    """
    This set of test will run only if straxen is installed and if we have access to the data
    The purpose of this test is to go through every correction, insert data into straxen and
    finally reprocess the data. If no errors come from this test then any changes in xedocs
    or straxen that could have affected this should have been caught by the tests.

    For single valued corrections we use random values
    Same for array corrections and dictionary corrections
    For map corrections we will have to use existing file maps
    """


    _run_test = True

    def setUp(self):

        self.db_name = "test_data" # "test_xedocs"
        self.db = pymongo.MongoClient()[self.db_name]  # database

        self.collections = {name: self.db[name] for name in
                            xedocs.list_schemas()}  # gives the xedocs collection to this db
        for collection in self.collections.values():
            collection.drop()

    def tearDown(self):
        for collection in self.collections.values():
            collection.drop()

    def save_test_data(self, docs, collection, schema, **kwargs):
        # saves all the data generated so we can access it via URLConfig
        
        # some of the correction involve interpolating so it is important we first organize the data in time    
        docs = sorted(docs, key=lambda x: x.time) 

        for doc1, doc2 in zip(docs[:-1], docs[1:]):
             #Require minimum 10 second spacing between samples
             #otherwise we get into trouble with rounding
             assume((doc2.time - doc1.time) > datetime.timedelta(seconds=10))

        
        new_docs = []
        if 'kind' in kwargs:
            # deals with data that are dictionary corrections
            if kwargs['kind'] == 'dict':
                
                # Make a copy of the original and change the partition to cd 
                for i in np.arange(len(docs)):
                    doc2 = docs[i].copy()
                    doc2.partition = 'cd'
                    new_docs.append(docs[i])
                    new_docs.append(doc2)
                    
                
            docs = new_docs
                
        saved_docs = []

        for i in np.arange(len(docs)):
            
            saved_docs.append(docs[i]) # insures we are only passing on data that is being saved
            docs[i].save(self.db[collection])  

        return saved_docs

    
    def check_insert_data(self, docs, collection, straxen_correction_name, plugin, schema):
        """
        Insures that the value inserted does not change
        """
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file)

        for j in np.arange(len(docs)):

            st_xd.set_config({straxen_correction_name: 'xedocs-test://'
                                                       '{correction}'
                                                       '?version={version}&time={time}'
                                                       '&attr=value'.format(version=docs[j].version,
                                                                            time=docs[j].time,
                                                                            correction=collection
                                                                            )
                              })
            correction_value = st_xd.get_single_plugin(run_id_nt, plugin)
            assert(getattr(correction_value, straxen_correction_name) == docs[j].value), f"The data generated in docs for correction {collection} does not match the inserted value"
    
    def check_insert_data_dict(self, docs, collection, straxen_correction_name, plugin, schema):
        # checks we are able to insert data into straxen from xedocs using URLConfigs
        # Due to the difference in URLConfig between the two a separate function was made
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)


        for j in np.arange(int(len(docs)/2)):
            
            st_xd.set_config({straxen_correction_name: 'objects-to-dict://xedocs-test://'
                                                       '{correction}'
                                                       '?version={version}&time={time}'
                                                       '&partition=["ab","cd"]'
                                                       '&key_attr=partition'
                                                       '&value_attr=value'.format(version=docs[2*j].version,
                                                                            time=docs[2*j].time,
                                                                            correction=collection
                                                                            )
                              })
            
            #print(schema.find())
            correction_value = st_xd.get_single_plugin(run_id_nt, plugin)
            
            assert(getattr(correction_value, straxen_correction_name)['ab'] == docs[2*j].value), f"The data generated in docs for correction {collection} does not match the inserted value"

    def check_reprocessing(self, docs, straxen_correction_name, collection, plugin):
        # Reprocess data in straxen with xedocs URLConfiguration
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        
        
        for j in np.arange(len(docs)):
            st_xd.set_config({straxen_correction_name: 'xedocs-test://'
                                                       '{correction}'
                                                       '?version={version}&time={time}'
                                                       '&attr=value'.format(version=docs[j].version,
                                                                            time=docs[j].time,
                                                                            correction=collection
                                                                            )
                              })
            data = st_xd.get_array(run_id_nt, plugin)

            assert(len(data) != 0), f"Data could not be generated with correction {collection}"
            
    def check_reprocessing_dict(self, docs, straxen_correction_name, collection, plugin):
        # Reprocess data in straxen with xedocs URLConfiguration 
        
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        for j in np.arange(int(len(docs)/2)):
            
            st_xd.set_config({straxen_correction_name: 'objects-to-dict://xedocs-test://'
                                                       '{correction}'
                                                       '?version={version}&time={time}'
                                                       '&partition=["ab","cd"]'
                                                       '&key_attr=partition'
                                                       '&value_attr=value'.format(version=docs[2*j].version,
                                                                            time=docs[2*j].time,
                                                                            correction=collection
                                                                            )
                              })
            data = st_xd.get_array(run_id_nt, plugin)

            assert(len(data) != 0), f"Data could not be generated with correction {collection}"

    
    ######## Single Value corrections #########
    
    
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.ElectronLifetime, value=floats))
    def test_elife_data_insertion_into_straxen(self, docs: List[xedocs.schemas.ElectronLifetime]) -> None:
        
        collection = "electron_lifetimes"
        plugin = "corrected_areas"
        straxen_correction_name = 'elife'
        schema = xedocs.schemas.ElectronLifetime
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema)
            
        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
        print('Check_insert_data did not fail?')
       
      

        
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.ElectronDriftVelocity, value=floats))
    def test_e_drift_velocity_data_insertion_into_straxen(self, docs: List[xedocs.schemas.ElectronDriftVelocity]) -> None:
        
        collection = "electron_drift_velocities"
        plugin = "event_positions"
        straxen_correction_name = 'electron_drift_velocity'
        schema = xedocs.schemas.ElectronDriftVelocity
        col = self.db[collection]
        col.drop()
        

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)

    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.RelativeLightYield, value=floats))
    def test_rel_light_yield_data_insertion_into_straxen(self, docs: List[xedocs.schemas.RelativeLightYield]) -> None:
        
        collection = "relative_light_yield"
        plugin = "corrected_areas"
        straxen_correction_name = 'rel_light_yield'
        schema = xedocs.schemas.RelativeLightYield
        col = self.db[collection]
        col.drop()
        

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
    
    
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.ElectronDiffusionCte, value=floats))
    def test_e_drift_time_gate_insertion_into_straxen(self, docs: List[xedocs.schemas.ElectronDiffusionCte]) -> None:
        
        collection = "electron_drift_time_gates"
        plugin = "event_positions"
        straxen_correction_name = 'electron_drift_time_gate'
        schema = xedocs.schemas.RelativeLightYield
        col = self.db[collection]
        col.drop()
        

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
      
    
     
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.BaselineSamplesNV, value=floats))
    def test_baseline_sample_nv_insertion_into_straxen(self, docs: List[xedocs.schemas.BaselineSamplesNV]) -> None:
        
        collection = "baseline_samples_nv"
        plugin = "records_nv"
        straxen_correction_name = 'baseline_samples_nv'
        schema = xedocs.schemas.BaselineSamplesNV
        col = self.db[collection]
        col.drop()
        

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
    
    
    ##### Single value corrections reprocessing ##########
    
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!") 
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.ElectronLifetime, value=floats))
    def test_elife_data_reprocessing_straxen(self, docs: List[xedocs.schemas.ElectronLifetime]):

        collection = "electron_lifetimes"
        plugin = "corrected_areas"
        straxen_correction_name = 'elife'
        schema = xedocs.schemas.ElectronLifetime
        col = self.db[collection]
        col.drop()
        
        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!") 
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.ElectronDriftVelocity, value=floats))
    def test_e_drift_velocity_data_reprocessing_straxen(self, docs: List[xedocs.schemas.ElectronDriftVelocity]) -> None:

        collection = "electron_drift_velocities"
        plugin = "event_positions"
        straxen_correction_name = 'electron_drift_velocity'
        schema = xedocs.schemas.ElectronDriftVelocity
        col = self.db[collection]
        col.drop()


        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!") 
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.RelativeLightYield, value=floats))
    def test_rel_light_yield_data_reprocessing_straxen(self, docs: List[xedocs.schemas.RelativeLightYield]) -> None:
        # print(docs[0])
        collection = "relative_light_yield"
        plugin = "corrected_areas"
        straxen_correction_name = 'rel_light_yield'
        schema = xedocs.schemas.RelativeLightYield
        col = self.db[collection]
        col.drop()
        # self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!") 
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.ElectronDiffusionCte, value=floats))
    def test_e_drift_time_gate_reprocessing_straxen(self, docs: List[xedocs.schemas.ElectronDiffusionCte]) -> None:
        # print(docs[0])
        collection = "electron_drift_time_gates"
        plugin = "event_positions"
        straxen_correction_name = 'electron_drift_time_gate'
        schema = xedocs.schemas.RelativeLightYield
        col = self.db[collection]
        col.drop()
        # self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
    
    #Reprocessing this takes way too long
    """
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    @settings(deadline=None)
    @given(time_sampled_correction_strategy(xedocs.schemas.BaselineSamplesNV, value=floats))
    def test_baseline_sample_nv_insertion_into_straxen(self, docs: List[xedocs.schemas.BaselineSamplesNV]) -> None:
        
        collection = "baseline_samples_nv"
        plugin = "records_nv"
        straxen_correction_name = 'baseline_samples_nv'
        schema = xedocs.schemas.BaselineSamplesNV
        col = self.db[collection]
        col.drop()
        

        saved_docs = self.save_test_data(docs, collection, schema)

        self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
    """   
    
    ########### Dictionary Corrections ###############
    
    @settings(deadline=None)
    @given(dict_correction_strategy(xedocs.schemas.SingleElectronGain, value=floats))
    def test_segain_data_insertion_into_straxen(self, docs: List[xedocs.schemas.SingleElectronGain]) -> None:

        collection = "se_gains"
        plugin = "corrected_areas"
        straxen_correction_name = 'se_gain'
        schema = xedocs.schemas.SingleElectronGain
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema, kind = 'dict')
            
        self.check_insert_data_dict(saved_docs, collection, straxen_correction_name, plugin, schema)
        
  
    @settings(deadline=None)
    @given(dict_correction_strategy(xedocs.schemas.AvgSingleElectronGain, value=floats))
    def test_ave_segain_data_insertion_into_straxen(self, docs: List[xedocs.schemas.AvgSingleElectronGain]) -> None:

        collection = "avg_se_gains"
        plugin = "corrected_areas"
        straxen_correction_name = 'avg_se_gain'
        schema = xedocs.schemas.AvgSingleElectronGain
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema, kind = 'dict')
            
        self.check_insert_data_dict(saved_docs, collection, straxen_correction_name, plugin, schema)
        
    @settings(deadline=None)
    @given(dict_correction_strategy(xedocs.schemas.RelExtractionEff, value=floats))
    def test_rel_extraction_eff_data_insertion_into_straxen(self, docs: List[xedocs.schemas.RelExtractionEff]) -> None:

        collection = "rel_extraction_effs"
        plugin = "corrected_areas"
        straxen_correction_name = 'rel_extraction_eff'
        schema = xedocs.schemas.RelExtractionEff
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema, kind = 'dict')
            
        self.check_insert_data_dict(saved_docs, collection, straxen_correction_name, plugin, schema)
    
    ######## Reprocessing Dictionary corrections #################
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    @settings(deadline=None)
    @given(dict_correction_strategy(xedocs.schemas.SingleElectronGain, value=floats))
    def test_segain_data_reprocessing_straxen(self, docs: List[xedocs.schemas.SingleElectronGain]) -> None:

        collection = "se_gains"
        plugin = "corrected_areas"
        straxen_correction_name = 'se_gain'
        schema = xedocs.schemas.SingleElectronGain
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema, kind = 'dict')
            
        self.check_reprocessing_dict(docs, collection, straxen_correction_name, plugin)
        
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")   
    @settings(deadline=None)
    @given(dict_correction_strategy(xedocs.schemas.AvgSingleElectronGain, value=floats))
    def test_ave_segain_data_reprocessing_straxen(self, docs: List[xedocs.schemas.AvgSingleElectronGain]) -> None:

        collection = "avg_se_gains"
        plugin = "corrected_areas"
        straxen_correction_name = 'avg_se_gain'
        schema = xedocs.schemas.AvgSingleElectronGain
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema, kind = 'dict')
            
        self.check_reprocessing_dict(docs, collection, straxen_correction_name, plugin)
        
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!") 
    @settings(deadline=None)
    @given(dict_correction_strategy(xedocs.schemas.RelExtractionEff, value=floats))
    def test_rel_extraction_eff_data_reprocessing_straxen(self, docs: List[xedocs.schemas.RelExtractionEff]) -> None:

        collection = "rel_extraction_effs"
        plugin = "corrected_areas"
        straxen_correction_name = 'rel_extraction_eff'
        schema = xedocs.schemas.RelExtractionEff
        elife_col = self.db[collection]
        elife_col.drop()
        self.db[collection]

        saved_docs = self.save_test_data(docs, collection, schema, kind = 'dict')
            
        self.check_reprocessing_dict(docs, collection, straxen_correction_name, plugin)
    
    
    #### Array Corrections #######
    """
    For the array correction it would take way too much time to check the data the same way as we did with single valued
    corrections. Instead I generated arrays that are used for checking the insertion and for reprocessing of the data
    """
    
    @settings(deadline=None)
    def test_pmt_correction_insertion_into_straxen(self) -> None:
        #print(docs[0])
        collection = "hit_thresholds"
        plugin = "lone_hits"
        straxen_correction_name = 'hit_min_amplitude'
        detector = 'tpc'
        schema = xedocs.schemas.HitThreshold
        elife_col = self.db[collection]
        elife_col.drop()
        
        # The data for these array corrections are saved in files as using hypothesis would take too long
        data = np.load("./test_data/pmt_corrections.npz")
        times = [datetime.datetime(2001,1,1,0,0),
                datetime.datetime(2001,1,1,1,0),
                datetime.datetime(2001,1,1,2,0)]
                
        #Go through all 3 files saved        
        for u in np.arange(len(data)):

            for v in np.arange(straxen.n_tpc_pmts):

                schema(version = "v*", time = times[u], pmt = v, value = data[f'arr_{u}'][v],
                       detector = detector).save(self.db[collection])
        saved_docs = schema.find(version = "v*", datasource = self.db[collection], detector = detector, time = times[1])
        
        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
        
        # if you have access to the data check reprocessing as well
        if straxen.utilix_is_configured():
            self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
    
   
    @settings(deadline=None)
    def test_nveto_correction_insertion_into_straxen(self) -> None:

        collection = "hit_thresholds"
        plugin = "lone_hits"
        straxen_correction_name = 'hit_min_amplitude'
        detector = 'neutron_veto'
        schema = xedocs.schemas.HitThreshold
        elife_col = self.db[collection]
        elife_col.drop()
        
        # The data for these array corrections are saved in files as using hypothesis would take too long
        data = np.load("./test_data/nveto_corrections.npz")
        times = [datetime.datetime(2001,1,1,0,0),
                datetime.datetime(2001,1,1,1,0),
                datetime.datetime(2001,1,1,2,0)]
        for u in np.arange(len(data)):

            for v in np.arange(straxen.n_nveto_pmts):

                schema(version = "v*", time = times[u], pmt = v, value = data[f'arr_{u}'][v],
                       detector = detector).save(self.db[collection])
        
        saved_docs = schema.find(version = "v*", datasource = self.db[collection], detector = detector, time = times[1])
        
        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
        
        # if you have access to the data check reprocessing as well
        if straxen.utilix_is_configured():
            self.check_reprocessing(docs, collection, straxen_correction_name, plugin)
            
        
    @settings(deadline=None)
    def test_mveto_correction_insertion_into_straxen(self) -> None:

        collection = "hit_thresholds"
        plugin = "lone_hits"
        straxen_correction_name = 'hit_min_amplitude'
        detector = 'muon_veto'
        schema = xedocs.schemas.HitThreshold
        elife_col = self.db[collection]
        elife_col.drop()
        
        data = np.load("./test_data/nveto_corrections.npz")
        times = [datetime.datetime(2001,1,1,0,0),
                datetime.datetime(2001,1,1,1,0),
                datetime.datetime(2001,1,1,2,0)]
        
        for u in np.arange(len(data)):

            for v in np.arange(straxen.n_mveto_pmts):

                schema(version = "v*", time = times[u], pmt = v, value = data[f'arr_{u}'][v],
                       detector = detector).save(self.db[collection])
        
        saved_docs = schema.find(version = "v*", datasource = self.db[collection], detector = detector, time = times[1])
        
        self.check_insert_data(saved_docs, collection, straxen_correction_name, plugin, schema)
        
        # if you have access to the data check reprocessing as well
        if straxen.utilix_is_configured():
            self.check_reprocessing(docs, collection, straxen_correction_name, plugin)

    
    
    ####### Map Corrections ##########
    """
    These corrections need to be handled differently from the rest as we do not have a nice way to generate
    this data, as such we will simply import 1 existing map for each and confirm we can reprocess with 
    this map.
    """
    
    def check_map_correction(self, algorithm, db_correction, schema, straxen_cor_name, xedocs_cor_name, config, **kwarg):
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        col = self.db[xedocs_cor_name]
        col.drop()
        self.db[xedocs_cor_name]
        doc = db_correction.find_one(version = 'v1', algorithm = algorithm)
        print(doc.value)
        
        new_doc = schema(version = 'v*', 
                         value = doc.value, 
                         algorithm = algorithm, 
                         time = doc.time)
        new_doc.save(self.db[xedocs_cor_name])
        assert(doc.value == schema.find(datasource = self.db[xedocs_cor_name], 
                                                         version = 'v*',
                                                         algorithm = algorithm,
                                                         time = doc.time)[0].value)
        
        if (straxen_cor_name == 's1_xyz_map') or (straxen_cor_name == 's2_xy_map'): 
            st_xd.set_config({straxen_cor_name:"itp_map://resource://xedocs-test://format://"
                                           "{xedocs_name}"
                                           "?version=v*&run_id={run_id}"
                                           "&algorithm={algo}&attr=value".format(xedocs_name = xedocs_cor_name,
                                                            algo = algorithm,
                                                            run_id = doc.time)})
            if straxen.utilix_is_configured():
                data = st_xd.get_array(run_id_nt, "corrected_areas")
                assert(len(data) != 0)
        
        
        elif straxen_cor_name == 'fdc_map':
            st_xd.set_config({straxen_cor_name:"itp_map://resource://xedocs-test://format://"
                                           "{xedocs_name}"
                                           "?version=v*&run_id={run_id}&fmt=binary"
                                           "&algorithm={algo}&attr=value".format(xedocs_name = xedocs_cor_name,
                                                            algo = algorithm,
                                                            run_id = doc.time)})
            if straxen.utilix_is_configured():
                data = st_xd.get_array(run_id_nt, "event_positions")
                assert(len(data) != 0)
            
     
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_s1_xyz_map_mlp_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('mlp', xd_db.corrections.s1_xyz_maps, 
                                  xedocs.schemas.S1XYZMap, 's1_xyz_map', 's1_xyz_maps',
                                  'event_info')
        
        
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")   
    def test_s1_xyz_map_cnn_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('cnn', xd_db.corrections.s1_xyz_maps, 
                                  xedocs.schemas.S1XYZMap, 's1_xyz_map', 's1_xyz_maps',
                                  'event_info')
        
        
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")    
    def test_s1_xyz_map_gcn_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('gcn', xd_db.corrections.s1_xyz_maps, 
                                  xedocs.schemas.S1XYZMap, 's1_xyz_map', 's1_xyz_maps',
                                  'event_info') 
        
        
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_s2_xy_map_mlp_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('mlp', xd_db.corrections.s2_xy_maps, 
                                  xedocs.schemas.S2XYMap, 's2_xy_map', 's2_xy_maps',
                                  'event_info')

    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_s2_xy_map_cnn_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('cnn', xd_db.corrections.s2_xy_maps, 
                                  xedocs.schemas.S2XYMap, 's2_xy_map', 's2_xy_maps',
                                  'event_info') 
        
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")    
    def test_s2_xy_map_gcn_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('gcn', xd_db.corrections.s2_xy_maps, 
                                  xedocs.schemas.S2XYMap, 's2_xy_map', 's2_xy_maps',
                                  'event_info') 
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_fdc_map_mlp_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('mlp', xd_db.corrections.fdc_maps, 
                                  xedocs.schemas.FdcMap, 'fdc_map', 'fdc_maps',
                                  'event_positions') 
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_fdc_map_cnn_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('cnn', xd_db.corrections.fdc_maps, 
                                  xedocs.schemas.FdcMap, 'fdc_map', 'fdc_maps',
                                  'event_positions') 
        
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")    
    def test_fdc_map_gcn_into_straxen(self) -> None:
        xd_db = xedocs.staging_db()
        self.check_map_correction('gcn', xd_db.corrections.fdc_maps, 
                                  xedocs.schemas.FdcMap, 'fdc_map', 'fdc_maps',
                                  'event_positions')
    
    
    # The corrections bellow simply did not have a presaved value in the database at the time so I just hard coded some
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!") 
    def test_s1_aft_xyz_into_straxen(self) -> None:
        
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        xd_db = xedocs.staging_db()
        schema = xedocs.schemas.S1AFTXYZMap
        xedocs_cor_name = 's1_aft_xyz_maps'
        value = 's1_aft_dd_xyz_XENONnT_kr-83m_08Feb2022.json'
        straxen_cor_name = 's1_aft_map'
        
        new_doc = schema(version = 'v*', 
                         value = value,
                         time = (datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
        new_doc.save(self.db[xedocs_cor_name])
        
        assert(value == schema.find(datasource = self.db[xedocs_cor_name], 
                                                         version = 'v*',
                                                         time = new_doc.time)[0].value)
        
        st_xd.set_config({straxen_cor_name:"itp_map://resource://xedocs-test://"
                                           "s1_aft_xyz_maps"
                                           "?version=v*&attr=value&fmt=json"})
        assert(len(st_xd.get_array(run_id_nt, 'event_pattern_fit')) != 0)
        

    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_bayes_model_mlp_into_straxen(self) -> None:
        
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        xd_db = xedocs.staging_db()
        schema = xedocs.schemas.NaiveBayesClassifier
        xedocs_cor_name = 'bayes_models'
        straxen_cor_name = 'bayes_config_file'
        value = 'conditional_probabilities_and_bins_v1_w_global_v6.npz'
        
        new_doc = schema(version = 'v*', 
                         value = value,
                         time = (datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
        new_doc.save(self.db[xedocs_cor_name])
        
        assert(value == schema.find(datasource = self.db[xedocs_cor_name], 
                                                         version = 'v*',
                                                         time = new_doc.time)[0].value)
        
        st_xd.set_config({straxen_cor_name:"resource://xedocs-test://"
                                           "bayes_models"
                                           "?version=v*&attr=value&fmt=npy"})
        if straxen.utilix_is_configured():
            assert(len(st_xd.get_array(run_id_nt, 'peak_classification_bayes')) != 0)
                                                         
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_posrec_mlp_into_straxen(self) -> None:
        
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        xd_db = xedocs.staging_db()
        schema = xedocs.schemas.PosRecModel
        algorithm = 'mlp'
        xedocs_cor_name = 'posrec_models'
        value = 'xnt_mlp_wfsim_20201214.tar.gz'
        straxen_cor_name = 'tf_model_mlp'
        
        new_doc = schema(version = 'v*', 
                         value = value,
                         kind = algorithm, 
                         time = (datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
        new_doc.save(self.db[xedocs_cor_name])
        assert(value == schema.find(datasource = self.db[xedocs_cor_name], 
                                                         version = 'v*',
                                                         kind = algorithm,
                                                         time = new_doc.time)[0].value)
        
        st_xd.set_config({straxen_cor_name:'tf://'
                                               'resource://'
                                               'xedocs-test://posrec_models'
                                               '?version=v*'
                                               '&run_id={run_id}'
                                               '&kind={algo}'
                                               '&attr=value'
                                               '&fmt=abs_path'.format(xedocs_name = xedocs_cor_name,
                                                                      algo = algorithm,
                                                                      run_id = new_doc.time)})
        
        if straxen.utilix_is_configured():
            assert(len(st_xd.get_array(run_id_nt, 'peak_positions_mlp')) != 0)
         
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_posrec_cnn_into_straxen(self) -> None:
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        st_xd.register(straxen.plugins.PeakPositionsCNN)
        xd_db = xedocs.staging_db()
        schema = xedocs.schemas.PosRecModel
        algorithm = 'cnn'
        xedocs_cor_name = 'posrec_models'
        value = 'xnt_cnn_wfsim_A_5_2000_20210112.tar.gz'
        straxen_cor_name = 'tf_model_cnn'
        
        new_doc = schema(version = 'v*', 
                         value = value,
                         kind = algorithm, 
                         time = (datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
        new_doc.save(self.db[xedocs_cor_name])
        assert(value == schema.find(datasource = self.db[xedocs_cor_name], 
                                                         version = 'v*',
                                                         kind = algorithm,
                                                         time = new_doc.time)[0].value)
        
        st_xd.set_config({straxen_cor_name:'tf://'
                                               'resource://'
                                               'xedocs-test://posrec_models'
                                               '?version=v*'
                                               '&run_id={run_id}'
                                               '&kind={algo}'
                                               '&attr=value'
                                               '&fmt=abs_path'.format(xedocs_name = xedocs_cor_name,
                                                                      algo = algorithm,
                                                                      run_id = new_doc.time)})
        
        if straxen.utilix_is_configured():
            assert(len(st_xd.get_array(run_id_nt, 'peak_positions_cnn')) != 0)
    
    @unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
    def test_posrec_gcn_into_straxen(self) -> None:
        st_xd = straxen.contexts.xenonnt_online(output_folder = output_file, include_rucio_remote=True,download_heavy=True)
        st_xd.register(straxen.plugins.PeakPositionsGCN)
        xd_db = xedocs.staging_db()
        schema = xedocs.schemas.PosRecModel
        algorithm = 'cnn'
        xedocs_cor_name = 'posrec_models'
        value = 'xnt_gcn_wfsim_20201203.tar.gz'
        straxen_cor_name = 'tf_model_cnn'
        
        new_doc = schema(version = 'v*', 
                         value = value,
                         kind = algorithm, 
                         time = (datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
        new_doc.save(self.db[xedocs_cor_name])
        assert(value == schema.find(datasource = self.db[xedocs_cor_name], 
                                                         version = 'v*',
                                                         kind = algorithm,
                                                         time = new_doc.time)[0].value)
        
        st_xd.set_config({straxen_cor_name:'tf://'
                                               'resource://'
                                               'xedocs-test://posrec_models'
                                               '?version=v*'
                                               '&run_id={run_id}'
                                               '&kind={algo}'
                                               '&attr=value'
                                               '&fmt=abs_path'.format(xedocs_name = xedocs_cor_name,
                                                                      algo = algorithm,
                                                                      run_id = new_doc.time)})
        
        if straxen.utilix_is_configured():
            assert(len(st_xd.get_array(run_id_nt, 'peak_positions_gcn')) != 0)
                                                                 

if __name__ == '__main__':
    unittest.main()

    