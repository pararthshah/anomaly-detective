# common interface for finding anomalies
import os, sys
if __name__=='__main__':
    sys.path.insert(0, "..")

import core.hmm as hmm
import core.naive as naive
import scripts.features as features
import core.anomalies as anomalies
from scripts.read_timeseries import read_lists
from scripts.ts_functions import bucketize, de_bucketize
from anomalies import max_anomalies
import match

def get_anomalies(path, algorithm, feature=None, window_size=15, mul_dev=3, n_states= 10, percent=2):
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
        times= times[window_size:len(times)-window_size]
        flist= bucketize(times, features.create_window_features(values, features.f_mean, window_size), bucket_size)
        mean_likelihoods= hmm.get_likelihoods(flist, n_states)
        flist= bucketize(times, features.create_window_features(values, features.f_var, window_size), bucket_size)
        var_likelihoods= hmm.get_likelihoods(flist, n_states)
        values= bucketize(times, values[window_size:len(values)- window_size], bucket_size)
        value_likelihoods= hmm.get_likelihoods(values, n_states)
        likelihoods= [mean_likelihoods[i] + var_likelihoods[i] + value_likelihoods[i] for i in range(0, len(values))]
        likelihoods= de_bucketize(times, likelihoods, bucket_size)
        return hmm.likelihoods_to_anomalies(times, likelihoods, float(percent)/100)
    elif algorithm=="mv":
        return match.machine_majority_vote(path, float(percent)/100) 
    elif algorithm=="tmv":
        return match.ts_majority_vote(path, float(percent)/100)
    elif algorithm== "optimal":
        anomaly=  match.optimize_timeseries(path, mul_dev= 3, percent= 0.5, top= None)[0]
        return anomaly
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
    print get_anomalies(path, "hmm")

