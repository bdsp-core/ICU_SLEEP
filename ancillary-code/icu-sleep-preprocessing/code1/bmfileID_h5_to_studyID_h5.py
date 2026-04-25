#!/usr/bin/python3

### after getting BM reserach data, there might still be data of other patients in those files.  here, we only select the data within ADT_TransferIn and ADT_TransferOut

import pandas as pd
import os
import h5py
import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code')
# sys.path.append('/home/wolfgang/repos/Bedmaster-ICU-tools/code/conversion')
from bmresearch_tools import *

# read in ICU-Sleep ICU-only table:
def main():

<<<<<<< HEAD
    study_ids_to_process = [116, 113]

    bmfileID_to_studyID(study_ids_to_process = study_ids_to_process)
=======
	# study_ids_to_process = [8, 27, 36, 43, 44, 185] # [3, 8, 15, 16, 18, 25, 27, 36, 43, 44, 45, 47, 64, 67, 68, 71, 163, 168, 185, 187]
	study_ids_to_process = [int(sys.argv[1])] # [8, 27, 36, 43, 44, 185]
	# study_ids_to_process = [76]

	bmfileID_to_studyID(study_ids_to_process = study_ids_to_process)
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

def bmfileID_to_studyID(study_ids_to_process=None, force_overwrite = 0):

	# import pdb; pdb.set_trace()
	#### config:
	# mad3drive = '/media/mad3/'
	mad3drive = 'M:'

	mad3folder = os.path.join(mad3drive,'Projects/ICU_SLEEP_STUDY/data/data_analysis')


	tablefile = 'Study/ICUSleep_DataTable_ICUonly.csv'
	fileid_h5_dir = os.path.join(mad3folder,'BMR_fileID/')      # input files dir

	# print('tMP')
	# mad3folder2 = 'C:/Users/wg984/Wolfgang/tmp'
	studyid_h5_dir = os.path.join(mad3folder,'BMR_studyID/')    # output files dir

	####

<<<<<<< HEAD
    for studyIDsel in study_ids_to_process:
        try:
=======
	table = pd.read_csv(os.path.join(mad3folder, tablefile))
	table.ADT_TransferIn = pd.to_datetime(table.ADT_TransferIn, infer_datetime_format=1)
	table.ADT_TransferOut = pd.to_datetime(table.ADT_TransferOut, infer_datetime_format=1)
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

	# loop over all patienmin(table_bm_file['ADT_TransferIn'])
	if study_ids_to_process is None:
		study_ids_to_process = pd.unique(table['StudyID'])

<<<<<<< HEAD
            if 'BMR_' + strstudyID + '.h5' in os.listdir(studyid_h5_dir) and not force_overwrite:
                # rename old file and run code again, create new file:
                os.rename(os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '.h5'),
                          os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '_missingdata_smallbundle.h5'))

            if force_overwrite: # then delete the file that already exists before writing on it.
                os.remove(os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '.h5'))
=======
	for studyIDsel in study_ids_to_process:
		try:
		# if 1:
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

			strstudyID = str(int(studyIDsel)).zfill(3)

			if 'BMR_' + strstudyID + '.h5' in os.listdir(studyid_h5_dir) and not force_overwrite:
				# rename old file and run code again, create new file:
				# os.rename(os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '.h5'),os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '_missingdata_smallbundle.h5') )
				os.rename(os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '.h5'),os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '_OldSortProcedure.h5') )

<<<<<<< HEAD
            table_studyID = table[table.StudyID == studyIDsel]
            # bm_files = pd.unique(table_studyID.BMFileID.dropna())

            bm_files1 = pd.unique(table_studyID.BMFileID.dropna())
            bm_files = []
            for x in bm_files1:
                bm_files += x.split(',')
            bm_files = pd.unique(bm_files)

            # loop over all bedmaster files for selected patient
            for bm_file in bm_files:
                print(bm_file)
                table_bm_file = table_studyID[[bm_file in x for x in table_studyID.BMFileID]]
                transfer_in = min(table_bm_file['ADT_TransferIn'])
                transfer_out = max(table_bm_file['ADT_TransferOut'])
                # print('transfer in: \t %s' % transfer_in)
                # print('transfer out: \t %s' % transfer_out)
=======
			# do not perform code:
				# continue  # if file already exists, code is not performed, unless force_overwrite is specified.

			if force_overwrite: # then delete the file that already exists before writing on it.
				os.remove(os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '.h5'))
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

			# if studyIDsel < 4 : continue # already done.
			print(strstudyID)

<<<<<<< HEAD
                signals_contained = get_metadata(bm_file_path)
                # loop over all signal contained in the specified bedmaster file
                for signal_sel in signals_contained:
                    data = BMR_load(bm_file_path, signals=[signal_sel], loadEvents=1)[signal_sel]
                    # do time_selection based on ADT transfers:
                    data = data[((data.datetime >= transfer_in) & (data.datetime <= transfer_out))]

                    # save to new .h5:
                    if data.shape[0] == 0:
                        continue  # nothing to do for empty signal.
                    else:
                        appendToHDF5file_studyID(data, signal_sel, output_h5_path)

=======
			output_h5_path = os.path.join(studyid_h5_dir, 'BMR_' + strstudyID + '.h5')
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

			table_studyID = table[table.StudyID == studyIDsel]
			bm_files1 = pd.unique(table_studyID.BMFileID.dropna())
			bm_files = []
			for x in bm_files1:
				bm_files += x.split(',')
			bm_files = pd.unique(bm_files)

			# sort bedmaster files according to ADT data and starting time of bedmaster file.
			# also use the ADT data related to a specific bedmaster file to do datetime selection.
			ADT_info_table = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/Study/ConversionStatus.csv'
			ADT_info_table = pd.read_csv(ADT_info_table)
			ADT_info_selection = ADT_info_table.loc[np.in1d(ADT_info_table.fileID, bm_files),:]
			ADT_info_selection = ADT_info_selection[['fileID','StartTime', 'EndTime', 'fileStartTime']]
			ADT_info_selection.sort_values(by=['StartTime', 'fileStartTime'], inplace=True)
			bm_files = ADT_info_selection.fileID.drop_duplicates()

			# loop over all bedmaster files for selected patient
			for bm_file in bm_files:
				print(bm_file)
				table_bm_file = ADT_info_selection[[bm_file in x for x in ADT_info_selection.fileID]]
				transfer_in = min(table_bm_file['StartTime'])
				transfer_out = max(table_bm_file['EndTime'])

				bm_file_path = os.path.join(fileid_h5_dir, bm_file +'.h5')

				if not os.path.exists(bm_file_path):
					print(f'{bm_file} is not available in studyID folder. continue')
					continue

				signals_contained = get_metadata(bm_file_path)
				# loop over all signal contained in the specified bedmaster file
				for signal_sel in signals_contained:
					data = BMR_load(bm_file_path, signals=[signal_sel], loadEvents=1)[signal_sel]
					# do time_selection based on ADT transfers:
					data = data[((data.datetime >= transfer_in) & (data.datetime <= transfer_out))]
					# save to new .h5:
					if data.shape[0] == 0 : continue # nothing to do for empty signal.
					else:
						appendToHDF5file_studyID(data, signal_sel, output_h5_path)

		except Exception as e:
			g = open("formatting_errorlog_bmfileID_to_studyID.txt", "a")
			g.write('\n ' + str(studyIDsel))
			g.write('\n ' + str(bm_file))
			g.write(str(e))
			g.close()
			continue


def appendToHDF5file_studyID(data, dset_name, output_h5_path):

	chunk_size = 64 # True

	with h5py.File(output_h5_path, 'a') as f:
		if not dset_name in f: # first write of this signal

			dsetVS = f.create_dataset(dset_name, data = data.signal.values.astype('float32'), shape=(data.signal.values.shape[0],), maxshape=(None,),
									  chunks=(chunk_size,), dtype='float32')
			dsetVS_dt = f.create_dataset(dset_name + '_dt',  data = data.posix.values.astype('float64'), shape=(data.signal.values.shape[0],), maxshape=(None,),
										 chunks=(chunk_size,), dtype='float64')
			dsetVS_event = f.create_dataset(dset_name + '_event',  data = data.event.values.astype('int8'), shape=(data.signal.values.shape[0],),
											maxshape=(None,),
											chunks=(chunk_size,),
											dtype='int8')
		else:
			f[dset_name].resize((f[dset_name].shape[0] + data.signal.values.shape[0]), axis = 0)

			# import pdb
			# pdb.set_trace()
			
			f[dset_name][-data.signal.values.shape[0]:] = data.signal.values.astype('float32')

			f[dset_name+'_dt'].resize((f[dset_name+'_dt'].shape[0] + data.signal.values.shape[0]), axis = 0)
			f[dset_name+'_dt'][-data.signal.values.shape[0]:] = data.posix.values.astype('float64')

			f[dset_name+'_event'].resize((f[dset_name+'_event'].shape[0] + data.signal.values.shape[0]), axis = 0)
			f[dset_name+'_event'][-data.signal.values.shape[0]:] = data.event.values.astype('int8')


if __name__ == '__main__':
	main()