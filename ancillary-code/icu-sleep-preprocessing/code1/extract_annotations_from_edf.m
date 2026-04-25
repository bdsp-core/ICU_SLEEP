T = readtable('C:/Users/wg984/Desktop/paths_annotation_rerun.csv','Delimiter',',');
for i=74:height(T)
    
    try
        directory_path = char(T{i,1})
        edf_path = char(T{i,2})
        hdr_deided = create_annotations(edf_path,directory_path);
        
    catch 
        fprintf('\n ###################################### error for this one!')
        i
        directory_path
        fprintf('continue with next')
    end
    
end