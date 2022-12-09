from typing import List
import xedocs
#from function_for_xedocs_test import *


import datetime
import pkg_resources
import pymongo
import numpy as np


from hypothesis import given, example, settings, assume
from hypothesis import strategies as st  # import integers, composite, SearchStrategy

######### Run id for testing data #############
run_id_nt = '047493'

output_file = './test_corrections'
#'/dali/lgrandi/lsanchez3/test_xedocs_data/rucio'


def round_datetime(dt):
    return dt.replace(microsecond=int(dt.microsecond / 1000) * 1000, second=0)

######### Sources to sample data from ##########

datetimes_vals = st.datetimes(
    min_value=datetime.datetime(2000, 1, 1, 0, 0),
    max_value=datetime.datetime(2231, 1, 1, 0, 0)).map(round_datetime)

floats = st.floats(
    min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False
)


###### Builds data to use in the corrections ##########
def time_sampled_correction_strategy(correction, **overrides):
    docs = st.lists(
        st.builds(correction,
                  version=st.just("v*"),
                  run_id=datetimes_vals,
                  **overrides),
        min_size=3,
        max_size=5,
        unique_by=lambda x: x.time
    )

    return docs

########## Data for array corrections #############

pmt_data = np.load("tests/pmt_corrections.npz")
nveto_data = np.load("tests/nveto_corrections.npz")
mveto_data = np.load("tests/mveto_corrections.npz")

time_for_array = [datetime.datetime(2001,1,1,0,0),
                  datetime.datetime(2001,1,1,1,0),
                  datetime.datetime(2001,1,1,2,0)]

########### Check for straxen and database settings ##############
installed = {pkg.key for pkg in pkg_resources.working_set}

# import straxen only if you have it
if 'straxen' in installed:
    import straxen

db_name = "test_data"  # "test_xedocs"
db = pymongo.MongoClient()[db_name]


######### Testing Protocol ################
@straxen.URLConfig.register("xedocs-test")
def protocol_test(name, context="test_data", sort=None, attr=None, **labels):
    import xedocs
    import pymongo

    db = pymongo.MongoClient()[context]

    schema = xedocs.find_schema(name)

    # filter out any not index labels
    index_fields = schema.get_index_fields()

    labels = {k: v for k, v in labels.items() if k in index_fields}

    # accessor = ctx[schema._CATEGORY][schema._ALIAS]

    # docs = accessor.find_docs(**labels)
    docs = schema.find(datasource=db[name], **labels)

    if not docs:
        raise KeyError(f"No matching documents found for {name}.")

    if isinstance(sort, str):
        docs = sorted(docs, key=lambda x: getattr(x, sort))
    elif sort:
        docs = sorted(docs)

    if attr is not None:
        docs = [getattr(d, attr) for d in docs]

    if len(docs) == 1:
        return docs[0]

    return docs

