import time
import h5py
import numpy as np
import pandas as pd
import os
import pytz
from datetime import datetime
from datetime import timedelta
import scipy.io as sio # .loadmat¶

import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
import plotly.io as pio
from plotly import tools
import matplotlib.pyplot as plt
import re
import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/conversion/')
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code')
from format_converted_to_research import load_BMfile, create_wv_dfdict, create_vs_dfdict, get_correctionToAddForThisBundle, applyBundleCorrection, natural_keys, appendToHDF5file
from qualitychecks_convertedfiles import *
import time


def main():
    format_multiple_bedmaster_files()

def format_multiple_bedmaster_files():

    print('started')
    # time.sleep(60*90)
    filedir = '//eris1fs2/CDAC/bedmaster_data/batching/ICUSleep_2/'
    filedir = '//eris1fs2/CDAC/bedmaster_data/batching/wg984_20200126_170310/'


    # savedir = 'C:/Users/wg984/Wolfgang/BedmasterDevelopment/'

    savedir = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_fileID'
    verbose = False

    # icu sleep file ids:
    files= 'C:/Users/wg984/Wolfgang/repos/ICU-Sleep/bedmaster_conversion/tosubmit.csv'
    files=pd.read_csv(files)
    filenames = files.fileID.to_list()

    # files = pd.read_csv('qualityChecksToDo.csv')
    # ff = open('quality_checks_errorlog_run5.txt','r')
    # ff0 = ff.read()
    # ff0 = ff0.replace('\n',' ')
    # ff0 = ff0.replace('\t',' ')
    # ff0 = ff0.split(' ')
    # ff0 = [x for x in ff0 if 'ELL' in x or 'BLK' in x]
    # ff1 = [re.split('_\d+_v4.mat', x)[0] for x in ff0]
    # filenames = np.unique(ff1)


    # num_of_files = files.shape[0]


    suffix = '_v4'

    # #microcheck:
    # filenames = [
    # 'BLK07_770-1565795532',
    # 'ELL04_404-1566264527',
    # 'BLK07_756-1565661060',
    # 'ELL04_406-1565831769',
    # 'BLK12_1254-1566194557',
    # # 'BLK10_1066-1561135440'
    # ]

    #erik sample files:
    # filenames = [
    # 'ELL09_912-1563979492',
    # 'BLK08_854-1549388188',
    # 'BLK08_854-1549581387'
    # ]

    for fileID in filenames:

        if fileID+'.h5' in os.listdir(savedir): #continue
            # rename old file and run code again, create new file:
            os.rename(os.path.join(savedir, fileID+'.h5'),os.path.join(savedir, 'BMR_' + fileID + '_missingdata.h5') )

        bundles = [x for x in os.listdir(filedir) if (fileID in x) and x.endswith(suffix+'.mat')]
        bundles.sort(key=natural_keys) # this will sort 1,2,3...9,10,11,.., and not 1,10,11,..,2,3
        # parts = [re.split(r'(_\d+_)', bundle)[1] for bundle in bundles]
        # parts = [int(re.split(r'(\d+)', part)[1]) for part in parts]
        parts = [re.split(r'(_\d+%s)'%(suffix+'.mat'), bundle)[1] for bundle in bundles]
        parts = [int(re.split(r'(\d+)', part)[1]) for part in parts]

        output_h5_path = os.path.join(savedir, fileID+'.h5')

        maxSegmentBundles = {}
        wv = {}
        vs = {}

        for bundle, part in list(zip(bundles, parts)):
            try:
                # if not part == 3:
                #     print(bundle)
                #     print('only specified bundle')
                #     continue
            # if 1:
                print(bundle)
                filepath = os.path.join(filedir, bundle)
                # load single BM bundle:
                [hdf5file, vs_signals, vs_time, vs_time_corrected, wv_signals, wv_time, wv_time_corrected, maxSegment] = load_BMfile(filepath, verbose = verbose ) # , load_all_signals = 0, vs_signals_toLoad = ['HR','SPO2%'], wv_signals_toLoad = ['ch7'])

                # print(maxSegment)
                maxSegmentBundles[part] = maxSegment
                correctionToAddForThisBundle_vs, lastCT_vs,correctionToAddForThisBundle_wv, lastCT_wv, maxSegmentBundles = get_correctionToAddForThisBundle(vs_time, vs_time_corrected, wv_time, wv_time_corrected,
                                                                                            maxSegmentBundles, part, verbose = verbose)
                # print('correctionToAddForThisBundle: ' + str(correctionToAddForThisBundle_vs))
                # print('LastCTwOverlap (uncorrected): '+ str(lastCT_vs))

                # create vs and wv dictionaries that contain dataframes for all signals:
                vs_singleBundle = create_vs_dfdict(vs_signals, vs_time_corrected, correctionToAddForThisBundle=correctionToAddForThisBundle_vs, lastCT_previousBundle=lastCT_vs)

                wv_singleBundle = create_wv_dfdict(wv_signals, wv_time, wv_time_corrected, correctionToAddForThisBundle=correctionToAddForThisBundle_wv, lastCT_previousBundle=lastCT_wv)

                # do quality checks:
                expected_vs_monoton = monotonicitycheck_vs(vs_singleBundle, verbose = verbose)
                expected_wv_monoton = monotonicitycheck_wv(wv_time_corrected, verbose = verbose)
                [expected_difference, max_difference, expected_behavior_event5] = compare_original_and_corrected_timestamps(vs_time, vs_singleBundle)

                if not all([(expected_vs_monoton == 1), (expected_wv_monoton == 1), (expected_difference == 1), (expected_behavior_event5 == 1)]):
                    errormsg = '\n' + bundle + \
                               '\t expected_vs_monotonicity: \t' + str(expected_vs_monoton) + \
                               '\t expected_wv_monotonicity: \t' + str(expected_wv_monoton) + \
                               '\t expected_difference: \t' + str(expected_difference) + \
                               '\t max_difference: \t' + str(max_difference) + \
                               '\t expected_behavior_event5: \t' + str(expected_behavior_event5)
                    g = open("quality_checks_errorlog_new_submission_after_missing_data.txt", "a")
                    g.write(errormsg)
                    g.close()

                appendToHDF5file(vs_singleBundle, output_h5_path)
                appendToHDF5file(wv_singleBundle, output_h5_path)

            except Exception as e:
                g = open("formatting_errorlog_new_submission_after_missing_data.txt", "a")
                g.write('\n ' + bundle)
                g.write(str(e))
                g.close()
                continue


if __name__ == '__main__':
    main()