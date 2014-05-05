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
    values = np.array(map(lambda x:x[1],series))
    s_ma = moving_avg(values,window)
    anomalies = []
    for i in range(window+1,len(series)-window):
        dist = abs(float(s_ma[i]-series[i][1]))
        if dist >= values.ptp()*threshold:
            anomalies.append((i, series[i][0], dist))
    if len(anomalies) <= 1:
        return map(lambda x:[x[1],x[1]], anomalies)
    intervals = []
    start = anomalies[0]
    end = start
    dist = anomalies[0][2]
    for val in anomalies[1:]:
        if val[0] - end[0] <= 4:
            end = val
            dist += val[2]
        else:
            intervals.append(([start[1]-100, end[1]+100], dist))
            start = val
            end = start
            dist = val[2]
    intervals.append(([start[1]-100, end[1]+100], dist))
    intervals.sort(key=lambda x:x[1],reverse=True)
    if len(intervals) > 100:
        intervals = intervals[:100]
    return map(lambda x:x[0], intervals)

