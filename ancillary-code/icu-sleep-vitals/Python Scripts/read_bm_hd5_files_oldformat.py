import pandas as pd
import numpy as np
import os
import sys
import h5py
import hdf5plugin
import path_config

print(h5py.__version__)
print(os.getcwd())

data_directory = r'L:/ConvertedData/bedmaster_pilot_cases/tensorization_results/cardiac_arrest_list/batch5/'  # location of tensorized bedmaster files
print(os.listdir(data_directory))

file = os.listdir(data_directory)[3]
filepath = os.path.join(data_directory, file)
print(filepath)
bmdata = h5py.File(filepath, "r")
print(bmdata.keys())
encounter_ids = list(bmdata['bedmaster'].keys())
print(encounter_ids)
bmdata['bedmaster'].keys()

encounter_id = encounter_ids[0]
print(bmdata['bedmaster'][encounter_id].keys())
print(bmdata['bedmaster'][encounter_id]['vitals'].keys())
print(bmdata['bedmaster'][encounter_id]['vitals']['hr'].keys())
# READ THE ACTUAL DATA:
print(bmdata['bedmaster'][encounter_id]['vitals']['hr']['value'][:])
print(bmdata['bedmaster'][encounter_id]['vitals']['hr']['time'][:])
print(bmdata['bedmaster'][encounter_id]['waveform']['i']['value'][:])