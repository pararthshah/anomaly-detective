import sys, os, numpy
sys.path.insert(0, "../")
from scripts.ts_functions import window_iter
from scripts.read_timeseries import read_timeseries, read_lists

class feature():
    def __init__(self, ts_name, feature_name, window_size, values):
        self.ts_name= ts_name
        self.feature_name= feature_name
        self.window_size= window_size
        self.values= values


# feature functions- given a window find the features over that window
def f_mean(window):
    return sum(window)/len(window)

def f_var(window):
    return numpy.var(numpy.array(window))

def f_deviance(window):
    return window[len(window)/2] - f_mean(window)

def f_slope(times, values):        # given a series (time value pairs), returns the slope of points over the series
    slope= list()
    for index in range(0, len(values)-1):
        slope.append(float(values[index+1] - values[index]))
    slope.append(slope[-1])
    return slope

def create_window_features(values, feature_func, window_size):
    window_size= window_size*2 + 1  # window_size in parameters is the number of points on either side of the considered point in a window
    featurelist= list()
    i=0
    for window in window_iter(values, window_size):
        featurelist.append(feature_func(window))
        i+= 1
    return featurelist


'''
def get_anomalies(path, mul_dev):
    times, values= read_lists(path)
    featurelist= create_window_features(values, f_mean, 15)
    #featurelist= f_slope(times, values)
    #return get_anomalies_from_series(times[0:len(featurelist)], featurelist, 3)
    return hmm.get_anomalies_from_series(times[0:len(featurelist)], featurelist, 10, 0.05)
'''

if __name__=="__main__":
    path= os.path.join(os.getcwd(), sys.argv[1]) 
    print get_anomalies(path, 3)
    '''
    series= read_timeseries(path)
    values= map(lambda x:x[1], series)
    feat1= create_window_features(values, 15, f_var)
    print feat1 
    '''

