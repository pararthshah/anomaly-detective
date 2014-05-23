# cannot be put in cluster.py due to cyclic imports

import sys
from scipy.cluster.vq import kmeans, vq
import numpy

if __name__=='__main__':
    sys.path.insert(0, "..")

import os, shutil, pprint
import random
import math
from scripts.read_timeseries import read_lists
import scripts.ts_functions as tsf
import server.config as config
import core.gateway as gateway
import core.cluster as cluster
import core.anomalies as anomalies

def cluster_anomalies(paths, n_clusters= 4, n_iter= 75):
    weight_lists= list()
    time_lists= list()
    index= 0
    for path in paths:
        anomaly_list= list() 
        for method, feature, w_size in gateway.algo_iter(methods=["naive"]):
            anomaly_list.append(gateway.get_anomalies(path, method, feature, percent=2, mul_dev= 3, window_size= w_size))
            print method, feature, w_size
        weights= anomalies.anomalies_to_weights(anomaly_list)
        #times, values= read_lists(path)
        if len(weights)== 0:
            weights= [0]
        weight_lists.append(weights)
        #time_lists.append(times)
        #del values
        print index, len(paths), len(weights), len(weight_lists[-1])
        index+= 1
    
    # pad all weight_lists with 0s to make them of equal length
    max_length= max([len(weights) for weights in weight_lists])
    
    for i, weights in enumerate(weight_lists):
        increase_length= max_length - len(weights)
        #if increase_length > 0: 
        weights.extend([0 for x in range(0, increase_length)])

    # find distance matrix
#    mat= [[cluster.non_normalized_distance(weights1, weights2) for weights2 in weight_lists] for weights1 in weight_lists]
#    pprint.pprint(mat) 
    # return cluster.cluster(weight_lists, n_clusters, n_iter, distance_func= cluster.non_normalized_distance)

    #cluster using numpy/ scipy
    np_wts= numpy.array([numpy.array(weights) for weights in weight_lists])
    centroids, _ = kmeans(np_wts, n_clusters)
    idx, _= vq(np_wts, centroids)
    print idx
    # convert idx to clusters
    clusters= [list() for i in range(0, n_clusters)]
    for i, c_no in enumerate(idx):
        clusters[c_no].append(i)
        
    return clusters


if __name__=='__main__':
    config.set_datadir(sys.argv[1])     # argv[1] is relative path to data directory
    cluster_dir= os.path.join(config.DATA_DIR, "anomaly_clusters")
    if not os.path.exists(cluster_dir):
        os.mkdir(cluster_dir)

    # get paths of all files in TS_DIR
    paths= [os.path.join(config.TS_DIR, fname) for fname in os.listdir(config.TS_DIR) if os.path.isfile(os.path.join(config.TS_DIR, fname))]
    pprint.pprint(paths)
    clusters= cluster_anomalies(paths, 4)
    #pprint.pprint(clusters)
    
    # now write each cluster to separate directory in cluster_dir
    for index, cluster in enumerate(clusters):
        curr_dir= os.path.join(cluster_dir, str(index))
        if not os.path.exists(curr_dir):
            os.mkdir(curr_dir)
        print len(cluster)
        for ts_index in cluster:
            shutil.copy(paths[ts_index], curr_dir)            

