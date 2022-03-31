Introduction
============

CMT2.0 is a reimplementation from scratch of CMT.

XeDocs is a collections of rframe schemas and utilities to help analysts store and access shared data.
The rframe framework was development to solve a number of issues that came up using the CMT tool.


    - Rigid indexing - all corrections are indexed by time only, requiring individual corrections for each PMT in the case of the pmt gains. This also limits the corrections database to only store time-dependent values, requiring other solutions for storing corrections without a time dependence.
    - Shared indexing - all versions of a single correction share the same time index, requiring special values (null) as a hack to have independent intervals of validity for each version. This complicates updating interpolated values like the pmt gains.
    - Inefficient use of MongoDB - the database is used as an object store for storing pandas dataframes, requiring the upload of the entire dataframe (for all times/versions) when updating a correction.
    - Hardcoded corrections - adding a new correction requires adding a new global version and releasing a new straxen version.
    - Single value storage - Each correction can only hold a single value, this prevent adding extra data fields (eg errors) and metadata fields (eg analyst name, creating date, description etc ) requiring a separate git repo just to store the metadata.
    - Global versions as strings - global versions are stored as json strings in a dedicated collection, no time dependence and adding new corrections requires a new global version. global versions have special status in CMT requiring extra code just to manage this collection. 

rframe and xedocs are conceptually similar to strax and straxen, where rframe is a general framework and xedocs
contains the specifc schemas and utility functions used by XENON analysts.


Remote Dataframes
-----------------

At its core CMT was supposed to be a simple way to have shared dataframe-like collections of data 
that can be accessed by all analysts and enforces certain rules on writing new data. To this end, 
the RemoteFrame was designed to behave similarly to a MultiIndex dataframe but selection operations 
are converted to database queries. The framework was designed to be extensible and allows adding support 
for special indexes or other data backends.

Currently supported data-backends:

    - MongoDB
    - Pandas dataframe
    - TinyDB
    - JSON record list
    - REST API

Currently implemented indexes:

    - Simple Index of any type, matches on exact values.
    - Interval Index of Datetime/Integer type, matches on interval overlap.
    - Sampled Index of Datetime/Integer/Float type, interpolation between sampled points, optional extrapolation.
