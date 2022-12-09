import pkg_resources
import datetime
import numpy as np

from hypothesis import assume

from .variables_for_test import time_for_array, db

installed = {pkg.key for pkg in pkg_resources.working_set}

if 'straxen' in installed:
    import straxen

    def save_test_data(docs, collection, db, **kwargs):
        # saves all the data generated so we can access it via URLConfig

        # some of the correction involve interpolating so it is important we first organize the data in time
        docs = sorted(docs, key=lambda x: x.time)

        for doc1, doc2 in zip(docs[:-1], docs[1:]):
            # Require minimum 10 second spacing between samples
            # otherwise we get into trouble with rounding
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
            saved_docs.append(docs[i])  # insures we are only passing on data that is being saved
            docs[i].save(db[collection])

        return saved_docs

    def create_array_docs(data, num_of_sensors, schema, detector, db, collection):
        for u in np.arange(len(data)):

            for v in np.arange(num_of_sensors):

                schema(version = "v*", time = time_for_array[u], pmt = v, value = data[f'arr_{u}'][v],
                       detector = detector).save(db[collection])

    def check_insert_data(docs, collection, straxen_correction_name, plugin, output_file, run_id_nt):
        """
        Insures that the value inserted does not change
        """
        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file)

        # we only need to check 3 docs so I need to cheat a little since I am getting a lot more
        # need to pass 1 array at a time
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
            assert (getattr(correction_value, straxen_correction_name) == docs[j].value), f"The data generated in docs for correction {collection} does not match the inserted value"

    def check_insert_data_dict(docs, collection, straxen_correction_name, plugin, output_file, run_id_nt):
        # checks we are able to insert data into straxen from xedocs using URLConfigs
        # Due to the difference in URLConfig between the two a separate function was made
        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file, include_rucio_remote=True,
                                                download_heavy=True)

        for j in np.arange(int(len(docs) / 2)):
            st_xd.set_config({straxen_correction_name: 'objects-to-dict://xedocs-test://'
                                                       '{correction}'
                                                       '?version={version}&time={time}'
                                                       '&partition=["ab","cd"]'
                                                       '&key_attr=partition'
                                                       '&value_attr=value'.format(version=docs[2 * j].version,
                                                                                  time=docs[2 * j].time,
                                                                                  correction=collection
                                                                                  )
                              })

            correction_value = st_xd.get_single_plugin(run_id_nt, plugin)

            assert (getattr(correction_value, straxen_correction_name)['ab'] == docs[
                2 * j].value), f"The data generated in docs for correction {collection} does not match the inserted value"

    def check_insert_array(docs, schema, detector, collection, straxen_correction_name, plugin, output_file, run_id_nt):
        """
        Insures that the value inserted does not change
        """
        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file)

        # get unique times in docs for check
        array_unique_time = time_for_array

        for j in np.arange(len(array_unique_time)):
            time_doc = schema.find(version='v*', detector= detector, time=array_unique_time[j], datasource = db[collection])

            st_xd.set_config({straxen_correction_name:'list-to-array://xedocs-test://'
                      '{collection}'
                      '?version=v*&time={time}&detector={detector}&attr=value'.format(version='v*',
                                                                               collection=collection,
                                                                               detector=detector,
                                                                               time=array_unique_time[j])})

            correction_value = st_xd.get_single_plugin(run_id_nt, plugin)
            data_array = np.zeros(len(time_doc))

            for t in np.arange(len(time_doc)):
                data_array[t] = time_doc[t].value

            assert (all(getattr(correction_value, straxen_correction_name) == data_array)), f"The data generated in docs for correction {collection} does not match the inserted value"

    def check_reprocessing(docs, straxen_correction_name, collection, plugin, output_file, run_id_nt):
        # Reprocess data in straxen with xedocs URLConfiguration
        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file, include_rucio_remote=True,
                                                download_heavy=True)

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

            assert (len(data) != 0), f"Data could not be generated with correction {collection}"


    def check_reprocessing_dict(docs, straxen_correction_name, collection, plugin, output_file, run_id_nt):
        # Reprocess data in straxen with xedocs URLConfiguration

        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file, include_rucio_remote=True,
                                                download_heavy=True)
        for j in np.arange(int(len(docs) / 2)):
            st_xd.set_config({straxen_correction_name: 'objects-to-dict://xedocs-test://'
                                                       '{correction}'
                                                       '?version={version}&time={time}'
                                                       '&partition=["ab","cd"]'
                                                       '&key_attr=partition'
                                                       '&value_attr=value'.format(version=docs[2 * j].version,
                                                                                  time=docs[2 * j].time,
                                                                                  correction=collection
                                                                                  )
                              })
            data = st_xd.get_array(run_id_nt, plugin)

            assert (len(data) != 0), f"Data could not be generated with correction {collection}"

    def check_reprocessing_array(docs, schema, detector, straxen_correction_name, collection, plugin, output_file, run_id_nt):
        # Reprocess data in straxen with xedocs URLConfiguration
        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file)

        array_unique_time = time_for_array

        for j in np.arange(len(array_unique_time)):
            time_doc = schema.find(version='v*', detector= detector, time=array_unique_time[j], datasource = db[collection])

            st_xd.set_config({straxen_correction_name:'list-to-array://xedocs-test://'
                      '{collection}'
                      '?version=v*&time={time}&detector={detector}&attr=value'.format(version='v*',
                                                                               collection=collection,
                                                                               detector=detector,
                                                                               time=array_unique_time[j])})

            data = st_xd.get_array(run_id_nt, plugin)

            assert (len(data) != 0), f"Data could not be generated with correction {collection}"


    def get_docs(schema, **kwarg):
        new_doc = []
        if 'value' not in kwarg:
            doc = kwarg['db_correction'].find_one(version='v1', algorithm=kwarg['algorithm'])
            if 'algorithm' in kwarg:
                new_doc = schema(version='v*',
                                 value=doc.value,
                                 algorithm=kwarg['algorithm'],
                                 time=doc.time)
            elif 'algorithm' not in kwarg:
                new_doc = schema(version='v*',
                                 value=doc.value,
                                 time=doc.time)
        # at the time of making these test not all correction have values already in xedocs so some I need to
        # take and hardcode myself, in the future the elif for value should not be necessary
        # we can simply delete this section at the time when this happens
        elif 'value' in kwarg:
            if 'algorithm' in kwarg:
                new_doc = schema(version='v*',
                                 value=kwarg['value'],
                                 algorithm=kwarg['algorithm'],
                                 time=(datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
            elif 'algorithm' not in kwarg:
                new_doc = schema(version='v*',
                                 value=kwarg['value'],
                                 time=(datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))

        return new_doc

    def get_docs_posrec(schema, **kwarg):
        new_doc = schema(version='v*',
                         value=kwarg['value'],
                         kind=kwarg['algorithm'],
                         time=(datetime.datetime(2017, 1, 1, 0, 0), datetime.datetime(2021, 1, 26, 17, 47, 44)))
        return new_doc


    def check_map_correction(schema, straxen_cor_name, xedocs_cor_name,
                         output_file, run_id_nt, db, plugin, **kwarg):
        # Maybe break down this functions in the future
        # moved algorithm and db_correction to kwargs

        st_xd = straxen.contexts.xenonnt_online(output_folder=output_file, include_rucio_remote=True,
                                                download_heavy=True)
        col = db[xedocs_cor_name]
        col.drop()

        if xedocs_cor_name == 'posrec_models':
            new_doc = get_docs_posrec(schema, **kwarg)

        else:
            new_doc = get_docs(schema, **kwarg)

        assert(new_doc, "please check the kwargs something went wrong with these inputs")
        new_doc.save(db[xedocs_cor_name])

        if (straxen_cor_name == 's1_xyz_map') or (straxen_cor_name == 's2_xy_map'):
            st_xd.set_config({straxen_cor_name: "itp_map://resource://xedocs-test://format://"
                                                "{xedocs_name}"
                                                "?version=v*&run_id={run_id}"
                                                "&algorithm={algo}&attr=value".format(xedocs_name=xedocs_cor_name,
                                                                                      algo=kwarg['algorithm'],
                                                                                      run_id=new_doc.time)})

            data = st_xd.get_array(run_id_nt, plugin)
            assert(len(data) != 0)

        elif straxen_cor_name == 'fdc_map':
            st_xd.set_config({straxen_cor_name: "itp_map://resource://xedocs-test://format://"
                                                "{xedocs_name}"
                                                "?version=v*&run_id={run_id}&fmt=binary"
                                                "&algorithm={algo}&attr=value".format(xedocs_name=xedocs_cor_name,
                                                                                      algo=kwarg['algorithm'],
                                                                                      run_id=new_doc.time)})
            if straxen.utilix_is_configured():
                data = st_xd.get_array(run_id_nt, plugin)
                assert (len(data) != 0)

        elif straxen_cor_name == 'fdc_map':
            st_xd.set_config({straxen_cor_name: "itp_map://resource://xedocs-test://format://"
                                                "{xedocs_name}"
                                                "?version=v*&run_id={run_id}&fmt=binary"
                                                "&algorithm={algo}&attr=value".format(xedocs_name=xedocs_cor_name,
                                                                                      algo=kwarg['algorithm'],
                                                                                      run_id=new_doc.time)})
            if straxen.utilix_is_configured():
                data = st_xd.get_array(run_id_nt, plugin)
                assert (len(data) != 0)

        elif straxen_cor_name == 's1_aft_map':
            st_xd.set_config({straxen_cor_name: "itp_map://resource://xedocs-test://"
                                                "s1_aft_xyz_maps"
                                                "?version=v*&attr=value&fmt=json"})
            if straxen.utilix_is_configured():
                assert (len(st_xd.get_array(run_id_nt, plugin)) != 0)

        elif straxen_cor_name == 'bayes_config_file':
            st_xd.set_config({straxen_cor_name: "resource://xedocs-test://"
                                                "bayes_models"
                                                "?version=v*&attr=value&fmt=npy"})
            if straxen.utilix_is_configured():
                assert (len(st_xd.get_array(run_id_nt, plugin)) != 0)

        elif straxen_cor_name == 'bayes_config_file':
            st_xd.set_config({straxen_cor_name: "resource://xedocs-test://"
                                                "bayes_models"
                                                "?version=v*&attr=value&fmt=npy"})
            if straxen.utilix_is_configured():
                assert (len(st_xd.get_array(run_id_nt, plugin)) != 0)

        elif xedocs_cor_name == 'posrec_models':
            st_xd.set_config({straxen_cor_name: 'tf://'
                                                'resource://'
                                                'xedocs-test://posrec_models'
                                                '?version=v*'
                                                '&run_id={run_id}'
                                                '&kind={algo}'
                                                '&attr=value'
                                                '&fmt=abs_path'.format(xedocs_name=xedocs_cor_name,
                                                                       algo=kwarg['algorithm'],
                                                                       run_id=new_doc.time)})
            if straxen.utilix_is_configured():
                assert (len(st_xd.get_array(run_id_nt, plugin)) != 0)
                
                
if 'cutax' in installed:
    import cutax
    
    def check_cutax_insert_data(docs, collection, straxen_correction_name, plugin, output_file, run_id_nt):
        """
        Insures that the value inserted does not change
        """
        st_xd = cutax.contexts.xenonnt_online(output_folder=output_file)

        for j in np.arange(len(docs)):
            st_xd.set_config({'diffusion_constant': 'xedocs-test://'
                                                    'electron_diffusion_cte'
                                                    '?version={version}'
                                                    '&time={time}&attr=value'.format(version=docs[j].version,
                                                                                       time=docs[j].time,
                                                                                       correction=collection
                                                                                       )})
            correction_value = st_xd.get_single_plugin(run_id_nt, plugin)
            assert (getattr(correction_value, straxen_correction_name) == docs[j].value), f"The data generated in docs for correction {collection} does not match the inserted value" 
            
    def check_reprocessing_cutax(docs, straxen_correction_name, collection, plugin, output_file, run_id_nt):
        # Reprocess data in straxen with xedocs URLConfiguration
        st_xd = cutax.contexts.xenonnt_online(output_folder=output_file, include_rucio_remote=True,
                                                download_heavy=True)

        for j in np.arange(len(docs)):
            st_xd.set_config({straxen_correction_name: 'xedocs-test://'
                                                       'electron_diffusion_cte'
                                                       '?version={version}'
                                                       '&time={time}&attr=value'.format(version=docs[j].version,
                                                                                     time=docs[j].time,
                                                                                     correction=collection
                                                                                     )})
            data = st_xd.get_df(run_id_nt, targets=('event_basics', plugin))

            assert (len(data) != 0), f"Data could not be generated with correction {collection}"
