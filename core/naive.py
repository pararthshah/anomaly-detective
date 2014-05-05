# just assumes gaussian distribution and returns anomalies
import math
import os, sys
from scripts.read_timeseries import read_timeseries
from scripts.ts_functions import bucketize
from scipy.stats import norm

def find_outliers(series, mul_dev=3):   # series is only values, not time value tuples
    n= len(series)
    mean= sum(series)/n
    sq_sum= sum(map(lambda x: x*x, series))
    variance= sq_sum/n - mean*mean
    sd= math.pow(variance, 0.5)
    # for now output points three s.d. away
    flagged= list()     # list of flagged indices
    for index, value in enumerate(series):
        if value < (mean -mul_dev*sd)  or value > (mean + mul_dev*sd):
            flagged.append(index)
    return flagged 

def get_anomalies(path, mul_dev):
    series= read_timeseries(path)
    factor= 15
    new_series= bucketize(series, len(series)/factor)
    outliers= find_outliers(new_series, mul_dev)
    index= 0
    anomalies= list()
    while index < len(outliers):
        start_time= series[outliers[index]*factor][0]
        while index < len(outliers)-1 and outliers[index + 1] == outliers[index] + 1:
            index+= 1
        end_time= series[outliers[index]*factor + 1][0]
        anomalies.append((start_time, end_time))
        index+= 1
    return anomalies

def get_anomalies_from_series(series, mul_dev):     # accepts a series instead of a path. Also does not bucketize list.
    series= read_timeseries(path)
    outliers= find_outliers(map(lambda x:x[1], series), mul_dev)
    index= 0
    anomalies= list()
    while index < len(outliers):
        start_time= series[outliers[index]][0]
        while index < len(outliers)-1 and outliers[index + 1] == outliers[index] + 1:
            index+= 1
        end_time= series[outliers[index] + 1][0]
        anomalies.append((start_time, end_time))
        index+= 1
    return anomalies

if __name__=='__main__':
    path= os.path.join(os.getcwd(), sys.argv[1])
    mul_dev= float(sys.argv[2])
    #anomalies= get_anomalies(path, mul_dev)
    anomalies= get_anomalies_from_series(read_timeseries(path), mul_dev)
    print anomalies
    print len(anomalies)

