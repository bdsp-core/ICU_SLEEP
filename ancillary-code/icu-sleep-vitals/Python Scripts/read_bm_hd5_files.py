import pandas as pd
import numpy as np
import os
import sys
import h5py

print(h5py.__version__)
print(os.getcwd())

data_directory = r'C:/Users/aj125/Dropbox (Partners HealthCare)/sample-bedmaster-hd5/' # location of tensorized bedmaster files'
print(os.listdir(data_directory))

file = os.listdir(data_directory)[0]
filepath = os.path.join(data_directory, file)
print(filepath)

bmdata = h5py.File(filepath, "r")
print(bmdata.keys())

list_of_keys = list(bmdata['bedmaster'].keys())
print(list_of_keys)
bmdata['bedmaster'].keys()

vitals = list_of_keys[0]
print(bmdata['bedmaster'][vitals].keys())

# READ THE ACTUAL DATA:
print(bmdata['bedmaster'][vitals]['hr']['value'][:])
print(bmdata['bedmaster'][vitals]['hr']['time'][:])

waveforms = list_of_keys[1]
print(bmdata['bedmaster'][waveforms].keys())

# READ THE ACTUAL DATA:
print(bmdata['bedmaster'][waveforms]['art1']['value'][:])
print(bmdata['bedmaster'][waveforms]['art1']['time'][:])
