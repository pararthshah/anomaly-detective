import math
import os, sys
sys.path.insert(0, "../")
from scripts.read_timeseries import read_timeseries, read_lists
from scripts.ts_functions import bucketize
#from scripts.features import create_window_features
from scipy.stats import norm

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

def index_to_interval(indices, times):     # converts a list of flagged indices to anomaly intervals
    anomalies= list()
    i= 0
    while i < len(indices):
        start_time= times[indices[i]]
        while i < len(indices)-1 and indices[i + 1] == indices[i] + 1:
            i+= 1
        end_time= times[min(len(times)-1, indices[i] + 1)]
        anomalies.append((start_time, end_time))
        i+= 1
    return anomalies

def get_anomalies(path, mul_dev, feature_func= None, window_size= 15):  # DEPRECATED
    # interface for server/code.py
    times, values= read_lists(path)
    featurelist= create_window_features(values, window_size, feature_func)  # add slope functionality
    outliers= find_outliers(featurelist, mul_dev)
    return index_to_interval(outliers, times)


def get_anomalies_from_series(times, values,  mul_dev):     # does not support bucketizing.
    # accepts a series instead of a path. Also does not bucketize list. Interface for scripts/ma.py and gateway.py
    if len(times) != len(values):
        raise Exception("times and values have different lengths: get_anomalies_from_series")
    outliers= find_outliers(values, mul_dev)
    return index_to_interval(outliers, times)


if __name__=='__main__':
    path= os.path.join(os.getcwd(), sys.argv[1])
    mul_dev= float(sys.argv[2])
    #anomalies= get_anomalies(path, mul_dev)
    anomalies= get_anomalies(path, mul_dev)
    print anomalies
    print len(anomalies)

