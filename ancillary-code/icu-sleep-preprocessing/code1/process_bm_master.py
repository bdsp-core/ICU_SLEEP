import pandas as pd
import numpy as np
import sys
sys.path.append("C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/")
sys.path.append("C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/user_files/")
from bmresearch_tools import BMR_load, BMR_plot, get_metadata
from bmfileID_h5_to_studyID_h5 import bmfileID_to_studyID
from format_multiple_bedmaster_files import format_multiple_bedmaster_files
from bedmaster_resample_waveforms import bedmaster_resample_waveforms
import matlab.engine
eng = matlab.engine.start_matlab()


def main():
	
	# + ### step 1. format bedmaster converted to bedmaster research:
	#  - input: a directory with files that need to be formatted.
	#  - output: each bedmaster fileID gets formatted. output with same fileID name .h5 (data_analysis/BMR_fileID/fileID.h5)
	# format_multiple_bedmaster_files()


	# + ### step 2. merge all bedmaster files for a patient, save the file as BMR_patientID.h5
	#  - input: formatted files from step1
	#  - output: BMR files for each subject (data_analysis/BMR_studyID/BMR_studyID.h5)
	# study_ids_to_process = [1,2,3]
	# bmfileID_to_studyID()

	# + ### step 3. resample waveforms (including ecg)
	#  - input: output from step2, i.e. BMR files for a patient
	#  - EKG gets resampled to 240Hz and gets saved in an .h5 with a slightly different format: signal array for each lead and startdatetime.
	#  - output: BMR_resampled_ECG/ECG_studyID.h5
	study_ids_to_process = [1,2,3,4]
	bedmaster_resample_waveforms(study_ids_to_process)

	# + ### step 4. HRV analysis.
	#  - input: resampled (evenly spaced, 240 Hz) ECG from step3
	#  - detects R peaks and runs HRV analysis
	#  - output: HRV_analysis/studyID_... .csv
	for study_id in study_ids_to_process:
		study_id = str(int(study_id)).zfill(3)
		force_overwrite = 0
		eng.HRV_Analysis_ICUSleepProject(study_id, force_overwrite, nargout=0)
		eng.quit()

if __name__ == '__main__':
	main()


