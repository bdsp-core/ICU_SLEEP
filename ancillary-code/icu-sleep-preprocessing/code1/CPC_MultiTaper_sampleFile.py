# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 15:28:28 2018

@author: wg984
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import os.path as op
import math
import matlab.engine


def main():
    CPC_MultiTaper()
    
def CPC_MultiTaper():
    
    MatlabEngine = matlab.engine.start_matlab()

    fs = 10
    windowsize = 60*8.5    # in seconds
    # increment = 60*4.25     # in seconds
    increment = 26          # 26sec is 5% of 8.5min window


    datadir = '//mad3/.../'

    MatlabEngine.MultiTaperFreqDomainAnalysis_includingCPC(datadir, windowsize, increment, fs, nargout=0)

if __name__ == "__main__":
    main()