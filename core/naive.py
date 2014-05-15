import math
import os, sys
sys.path.insert(0, "../")
from scripts.read_timeseries import read_timeseries, read_lists
from scripts.ts_functions import bucketize
from scipy.stats import norm
import anomalies as anomalies

def find_outliers(values, mul_dev=3): 
    # accepts list of values, and returns list of flagged indices
    n= len(values)
    mean= sum(values)/n
    sq_sum= sum(map(lambda x: x*x, values))
    variance= sq_sum/n - mean*mean
    sd= math.pow(variance, 0.5)
    # for now output points three s.d. away
    flagged= list()     # list of flagged indices
    for index, value in enumerate(values):
        if value < (mean -mul_dev*sd)  or value > (mean + mul_dev*sd):
            flagged.append(index)
    return flagged 

def get_anomalies_from_series(times, values,  mul_dev):     # does not support bucketizing.
    # accepts a series instead of a path. Also does not bucketize list. Interface for scripts/ma.py and gateway.py
    if len(times) != len(values):
        raise Exception("times and values have different lengths: get_anomalies_from_series")
    outliers= find_outliers(values, mul_dev)
    return anomalies.index_to_interval(outliers, times)


if __name__=='__main__':
    path= os.path.join(os.getcwd(), sys.argv[1])
    mul_dev= float(sys.argv[2])
    #anomalies= get_anomalies(path, mul_dev)
    anomalies= get_anomalies(path, mul_dev)
    print anomalies
    print len(anomalies)

