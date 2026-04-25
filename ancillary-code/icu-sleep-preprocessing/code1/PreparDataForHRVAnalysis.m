function [NN, tNN, tWin,AFWindows,out] = PreparDataForHRVAnalysis(rr,t,annotations,sqi,HRVparams,subjectID)

    out = []; % Struct used to save DFA and MSE preprocessed data
 
    % Exclude undesiderable data from RR series (i.e., arrhytmia, low SQI, ectopy, artefact, noise)
    [NN, tNN] = RRIntervalPreprocess(rr,t,annotations, HRVparams);  
    tWin = CreateWindowRRintervals(tNN, NN, HRVparams);    % Create Windows for Time and Frequency domain 
    
    % Create Windows for MSE and DFA and preprocess
    if HRVparams.MSE.on || HRVparams.DFA.on
       % Additional pre-processing to deal with missing data for MSE and DFA analysis     
       [out.NN_gapFilled, out.tNN_gapFilled] = RR_Preprocessing_for_MSE_DFA( NN, tNN );
    end
    if HRVparams.MSE.on
       out.tWinMSE = CreateWindowRRintervals(out.tNN_gapFilled, out.NN_gapFilled, HRVparams,'mse');
    end
    if HRVparams.DFA.on
        out.tWinDFA = CreateWindowRRintervals(out.tNN_gapFilled, out.NN_gapFilled, HRVparams,'dfa');
    end    
    
    % 2. Atrial Fibrillation Detection
    if HRVparams.af.on 
        [AFtest, AfAnalysisWindows] = PerformAFdetection(subjectID,t,rr,sqi,HRVparams);
        % fprintf('AF analysis completed for subject %s \n', subjectID);
        % Remove RRAnalysisWindows contating AF segments
        [tWin, AFWindows]= RemoveAFsegments(tWin,AfAnalysisWindows, AFtest,HRVparams);
        if HRVparams.MSE.on
            out.tWinMSE = RemoveAFsegments(out.tWinMSE,AfAnalysisWindows, AFtest,HRVparams);
        end
        if HRVparams.DFA.on 
            out.tWinDFA = RemoveAFsegments(out.tWinDFA,AfAnalysisWindows, AFtest,HRVparams);
        end
    else
        AFWindows = [];
    end
    
end