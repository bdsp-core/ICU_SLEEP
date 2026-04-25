function [C,phi,S12,S1,S2,t,f] = MultiTaperFreqDomainAnalysis_includingCPC2(dataNN, dataResp, windowsize, increment, Fs)

windowsize = double(windowsize);
increment = double(increment);
Fs = double(Fs);

dataNN = dataNN';
dataResp = dataResp';

% respiration and NN/RR data. each one-dimensional and same length.

% set params
params.movingwin=[windowsize, increment];      % [winLength, stepSize] in sec
params.tapers=[3 5];          % [time-bandwidth product, number of tapers] % 
params.fpass=[0.01 1];        % freq. range %
params.Fs=Fs;                 % sampling rate %

% compute coherence,phi,crossspectrum, powerspectra. Uses 'Chronux'
% Toolbox.
[C,phi,S12,S1,S2,t,f]=cohgramc(dataNN,dataResp,params.movingwin,params);

% csvwrite( datadir + string('Coherence.csv') , C' );
% csvwrite( datadir +  string('phi.csv') , phi' );
% csvwrite( datadir +  string('CrossPower.csv') , abs(S12') );
% csvwrite( datadir +  string('PowerSpectrogramNN.csv') , S1' );
% csvwrite( datadir +  string('PowerSpectrogramResp_ChestAbd.csv') , S2' );
% csvwrite( datadir +  string('time.csv'), t');
% csvwrite( datadir +  string('frequency.csv'), f');
% csvwrite( datadir +  string('CPC.csv'), CPC');

    % CPC = abs(C.*conj(C) .* S12);

% csvwrite( datadir +  string('Coherence.csv') , C' );
% csvwrite( datadir +  string('phi.csv') , phi' );
% csvwrite( datadir +  string('CrossPower.csv') , abs(S12') );
% csvwrite( datadir +  string('PowerSpectrogramNN.csv') , S1' );
% csvwrite( datadir +  string('PowerSpectrogramResp_ChestAbd.csv') , S2' );
% csvwrite( datadir +  string('time.csv'), t');
% csvwrite( datadir +  string('frequency.csv'), f');
% csvwrite( datadir +  string('CPC.csv'), CPC');


 