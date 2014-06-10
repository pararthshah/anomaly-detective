# common interface for finding anomalies
import os, sys
if __name__=='__main__':
    sys.path.insert(0, "..")
from numpy import array, std, mean, absolute, maximum, amax, var
import core.hmm as hmm
import core.naive as naive
import scripts.features as features
import core.anomalies as anomalies
from scripts.read_timeseries import read_lists
from scripts.ts_functions import bucketize, de_bucketize, bucket_iter
from anomalies import max_anomalies, ordered_min_anomalies 
import match
import core.cascade as cascade

def get_anomalies(path, algorithm, feature=None, window_size=15, mul_dev=3, n_states= 10, percent=2, base=512, levels=1):
    # mul_dev to be used for naive, percent for hmm. TODO: Use common metric for both.
    times, values= read_lists(path)

    if feature== "mean":
        flist= features.create_window_features(values, features.f_mean, window_size)
        times= times[window_size:len(times)-window_size]
    elif feature== "var":
        flist= features.create_window_features(values, features.f_var, window_size)
        times= times[window_size:len(times)-window_size]
    elif feature== "slope":
        flist= features.f_slope(times, values)      #TODO: bucketize/ smoothen? update: smoothening doesn't work
        times= times[:-1]
    elif feature== "deviance":
        flist= features.create_window_features(values, features.f_deviance, window_size)
        times= times[window_size:len(times)-window_size]
    elif feature== None:
        flist= values
    else:
        raise Exception("Unknown feature attribute in gateway.py")

    if algorithm== "hmm":
        bucket_size= 15
        flist= bucketize(times, flist, bucket_size)
        likelihoods= hmm.get_likelihoods(flist, n_states) 
        likelihoods= de_bucketize(times, likelihoods, bucket_size)
        #print likelihoods
        #return hmm.likelihoods_to_anomalies(times, likelihoods, float(percent)/100)    
        return anomalies.min_anomalies(times, likelihoods, float(percent)/100)

    elif algorithm== "naive":
        return naive.get_anomalies_from_series(times, flist, mul_dev)

    elif algorithm=="combined_hmm":
        bucket_size= 15
        if len(values) < 4000:  # hardcoded hack!
            bucket_size= 0
        times= times[window_size:len(times)-window_size]
        # mean
        flist= bucketize(times, features.create_window_features(values, features.f_mean, window_size), bucket_size)
        mean_likelihoods= hmm.get_likelihoods(flist, n_states)
        # var
        flist= bucketize(times, features.create_window_features(values, features.f_var, window_size), bucket_size)
        var_likelihoods= hmm.get_likelihoods(flist, n_states)
        # deviance
        flist= bucketize(times, features.create_window_features(values, features.f_deviance, window_size), bucket_size)
        dev_likelihoods= hmm.get_likelihoods(flist, n_states)
        # slope
        #flist= bucketize(times, features.create_window_features(values, features.f_deviance, window_size), bucket_size)
        flist= features.f_slope(times, values)
        flist= bucketize(times, flist[window_size:len(flist)-window_size], bucket_size)
        slope_likelihoods= hmm.get_likelihoods(flist, n_states)
        # actual values
        values= bucketize(times, values[window_size:len(values)- window_size], bucket_size)
        value_likelihoods= hmm.get_likelihoods(values, n_states)
        mean_std= std(array(mean_likelihoods))
        var_std= std(array(var_likelihoods))
        dev_std= std(array(dev_likelihoods))
        slope_std= std(array(slope_likelihoods))
        value_std= std(array(value_likelihoods))
        likelihoods= [mean_likelihoods[i]/mean_std + var_likelihoods[i]/var_std + dev_likelihoods[i]/dev_std + slope_likelihoods[i]/slope_std +  value_likelihoods[i]/value_std for i in range(0, len(values))]
        likelihoods= de_bucketize(times, likelihoods, bucket_size)
        ordered_anomalies, overlaps =  anomalies.ordered_min_anomalies(times, likelihoods, ratio= 0.005)
        return sorted(anomalies.min_cutoff(ordered_anomalies, overlaps))
        #return anomalies.min_anomalies(times, likelihoods, ratio= 0.005)
    elif algorithm=="mv":
        return match.machine_majority_vote(path, float(percent)/100) 
    elif algorithm=="tmv":
        return match.ts_majority_vote(path, float(percent)/100)
    elif algorithm== "optimal":
        anomaly=  match.optimize_timeseries(path, mul_dev= 3, percent= 1.5, top= None)[0]
        return anomaly
    elif algorithm == "cascade":
        return cascade.compute_anomalies1(times, values, base=base, levels=levels)
    elif algorithm== "var_based":
        s= avg_std(values)
        print s
        if s > 0.0010:
            print "combined_hmm"
            return get_anomalies(path, "combined_hmm", feature, window_size, mul_dev, n_states, percent, base, levels)
        else:
            print "optimal"
            return get_anomalies(path, "optimal", feature, window_size, mul_dev, n_states, percent, base, levels)
    else:
        raise Exception("Unknown algorithm attribute in gateway.py")
    
def normalized_std(values):
    numval= array(values)
    m= mean(numval)
    for i in range(0, len(values)):
        numval[i]= numval[i]- m
    sd= std(numval)
    for i in range(0, len(values)):
        numval[i]= numval[i]/sd
    grad= gradient(numval)
    return std(grad)
    
def avg_std(values, window_size= 10, bucket_size= 20):
    numval= array(values)
    m= mean(numval)
    for i in range(0, len(values)):
        numval[i]= numval[i]- m
#    sd= std(numval)
#    for i in range(0, len(values)):
#        numval[i]= numval[i]/sd
    maxnum= amax(absolute(numval))
    for i in range(0, len(values)):
        numval[i]= numval[i]/maxnum
    variance= 0
    n= 0
    for (start, end) in bucket_iter(bucket_size, len(numval)):
        variance+= var(numval[start:end])
        n+= 1
    return variance/n

def avg_slope(times, values):
    flist= features.create_window_features(values, features.f_mean, window_size)
    times= times[window_size:len(times)-window_size]
    flist= features.f_slope(times, values)      #TODO: bucketize/ smoothen? update: smoothening doesn't work

def get_likelihoods(name, path, base=512, levels=4):
    if name == "cascade":
        times, values = read_lists(path)
        likelihoods = cascade.compute_likelihoods(times, values, base, levels)
        return likelihoods
    else:
        raise Exception("Unknown algorithm attribute in gateway.py")    

class algo_iter:
    def __init__(self, methods= ["naive", "hmm"], features=[None, "mean", "var", "deviance"], window_sizes= [15, 30]):    
        self.algo_list= [(x, y, z) for z in window_sizes for y in features for x in methods]
        self.counter= -1
    
    def __iter__(self):
        return self

    def next(self):
        self.counter+= 1
        if self.counter < len(self.algo_list):
            return self.algo_list[self.counter]
        else:
            raise StopIteration

if __name__=="__main__":
    path= os.path.join(os.getcwd(), sys.argv[1])
    print get_anomalies(path, "cascade", base=64, levels=7)

