# from mike-l

#install.packages('comorbidity')
library(comorbidity)

file_list = list.files("C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/Data/Diagnosis_ICDs/test", pattern=NULL, all.files=FALSE, full.names=FALSE)
output_folder = list.files("C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/Data/Diagnosis_ICDs/test"
input_folder = "C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/Data/Diagnosis_ICDs/test"
output_prefix = "CCI_"
for (file in file_list){
  
  if (grepl(".csv", file, fixed = TRUE)[1] == TRUE ){
    
    print(file)
  
    input_name <- paste(c(input_folder, file),collapse = '')
    output_name <- paste(c(output_folder, output_prefix,  file),collapse = '')
    if (file.exists(output_name)){
      zz = 2
    }
    else{
      data <- read.csv2(input_name,sep = "," )
      charlson <- comorbidity(x = data, id = "MRN", code = "CurrentICD10ListTXT", score = "charlson", icd = "icd10", assign0 = FALSE)
      write.csv(charlson, output_name, row.names = F, quote = T)
      print(output_name)
      print('done')
      print('')
      
    }
    
  }
  
}



# Sub-in file from dropbox/data_diagnosis/EncounterDiagnosis_Inpatient_ADT_20200428080000.csv
#data2 <- read.csv2("D:/Dropbox (Partners HealthCare)/COVID_RISK_PREDICTION/data_diagnosis/EncounterDiagnosis_RIC_ED_visits_20200509080000.csv",sep = "," )
#charlson <- comorbidity(x = data2, id = "MRN", code = "CurrentICD10ListTXT", score = "charlson", icd = "icd10", assign0 = FALSE)
#write.csv(charlson, "D:/Dropbox (Partners HealthCare)/COVID_RISK_PREDICTION/data_CCI/CCI_RIC_ED_visits_20200509080000.csv", row.names = F, quote = T)
# Rscript script.R
