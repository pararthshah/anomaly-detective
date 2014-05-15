# common interface for finding anomalies
import os, sys
import core.hmm as hmm
import core.naive as naive
import scripts.features as features
import core.anomalies as anomalies
from scripts.read_timeseries import read_lists
from scripts.ts_functions import bucketize, de_bucketize
from anomalies import max_anomalies

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
        return majority_vote(path, float(percent)/100) 
    else:
        raise Exception("Unknown algorithm attribute in gateway.py")
    
# TODO: move to match.py after resolving cyclic dependencies
def majority_vote(path, ratio):    # reads file containing machine weights and returns anomalies
    # TODO: hacky way, improve
    ts_name= os.path.basename(path)
    dir_name= os.path.dirname(path)
    machine_name= ts_name.split("-")[0]
    weights_path= os.path.join(dir_name, "..", "machine_weights", machine_name)
    weights= [int(line.strip()) for line in open(weights_path, 'r')]
    anomalies= max_anomalies(range(0, len(weights)), weights, ratio)
    return anomalies

if __name__=="__main__":
    path= os.path.join(os.getcwd(), sys.argv[1])
    print get_anomalies(path, "hmm")

