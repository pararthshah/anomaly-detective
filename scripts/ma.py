#!/usr/bin/python

import numpy as np
from read_timeseries import read_timeseries

#dataset = [1,5,7,2,6,7,8,2,2,7,8,3,7,3,7,3,15,6]

def moving_avg(values,window):
    weigths = np.repeat(1.0, window)/window
    #including valid will REQUIRE there to be enough datapoints.
    #for example, if you take out valid, it will start @ point one,
    #not having any prior points, so itll be 1+0+0 = 1 /3 = .3333
    smas = np.convolve(values, weigths, 'valid')
    return smas # as a numpy array

#Will print out a 3MA for our dataset
#print movingaverage(dataset,3)

def detect_SMA(path, window, threshold):
    series = read_timeseries(path)
    s_ma = moving_avg(np.array(map(lambda x:x[1],series)),window)
    anomalies = []
    for i in range(window+1,len(series)-window):
        if abs(float(s_ma[i]-series[i][1])) >= threshold:
            anomalies.append([series[i][0],series[i][0]])
    return anomalies
