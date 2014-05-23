import os, shutil
import sys
import random
import math
from scripts.read_folder import read_folder
import scripts.ts_functions as tsf
import server.config as config
import anomalies

def cluster(slist, n_clusters, n_iter, distance_func= None): # slist should be a list(list(values)) or list(values)
    # implement in memory k means clustering for now
    n_lists= len(slist)
    if distance_func==None:
        global distance
        distance_func= distance

    # divide slist into n clusters: randomly choose n_clusters points from slist as centroids
    rand_pts= [random.randint(0, n_lists-1) for i in range(0, n_clusters)]
    centroids= [slist[i] for i in rand_pts]

    for i in range(0, n_iter):
        # assign every point to a centroid
        clusters= [list() for i in range(0, n_clusters)]
        for index, series in enumerate(slist):
            min_dist= float('inf') 
            min_centroid= -1
            for c_index, centroid in enumerate(centroids):
                dist= distance_func(centroid, series)
                if(min_dist > dist):
                    min_dist= dist
                    min_centroid= c_index
            clusters[min_centroid].append(index)

        # find centroid of every cluster
        for c_index in range(0, n_clusters):
            if len(clusters[c_index]) == 0:
                continue
            cluster_points= [slist[point] for point in clusters[c_index]]
            # find centroid of cluster_points
            centroids[c_index]= find_centroid(cluster_points)

    # convert indices to points?    
    return clusters
    
    
def distance(ts1, ts2):     # find distance between two timeseries
    if type(ts1) is list and type(ts2) is list:
        # normalize timeseries
        nts1= normalize(ts1)
        nts2= normalize(ts2)
        dist= 0 
        for (pt1, pt2) in zip(nts1, nts2):
            dist+= (pt1 - pt2)*(pt1 - pt2)
        return math.sqrt(dist)
    else:
        return math.sqrt(math.pow((ts1 - ts2), 2))

def non_normalized_distance(ts1, ts2):     # find distance between two timeseries
    if type(ts1) is list and type(ts2) is list:
        dist= 0 
        for (pt1, pt2) in zip(ts1, ts2):
            dist+= (pt1 - pt2)*(pt1 - pt2)
        return math.sqrt(dist)

def normalize(ts):  # normalizes by dividing my max
    max_ts= max(ts)
    if(max_ts != 0):
        return map(lambda x:x/max_ts, ts)
    else:
        return ts
    

def find_centroid(cluster): # for now simply finds the average of timeseries
    n_series= len(cluster)
    if type(cluster[0]) is list:
        avg_series= [0]*len(cluster[0])
        for series in cluster:
            for index, point in enumerate(series):
                avg_series[index]+= point
        avg_series= map(lambda x:x/n_series, avg_series)
        return avg_series

    else:
        return sum(cluster)/len(cluster)
    
def find_cluster(clusters, index):  # returns index in clusters which contains "index"
    for i, cluster in enumerate(clusters):
        if index in cluster:
            return i
    return -1
    
''' 
def cluster_anomalies(paths, n_clusters= 5):
    weight_lists= list()
    time_lists= list()

    for path in paths:
        anomaly_list= list() 
        for method, feature, w_size in gateway.algo_iter():
            anomaly_list.append(gateway.get_anomalies(path, method, feature, percent=2, mul_dev= 3, window_size= w_size))
        weight_lists.append(anomalies_to_weights(anomaly_list))
        times, values= read_timeseries(path)
        time_lists.append(times)
        del values
    
    # normalize times for all weight lists
    timevalues, weight_lists= combine(time_lists, weight_lists, 1000)

    # cluster weight_lists
    return cluster(weight_lists, n_clusters, 20, distance_func= non_normalized_distance)


if __name__=='__main__':
    sys.path.insert(0, "..")
    config.set_datadir(sys.argv[1])     # argv[1] is relative path to data directory
    cluster_dir= os.path.join(config.DATA_DIR, "anomaly_clusters")
    os.mkdir(cluster_dir)

    # get paths of all files in TS_DIR
    paths= [os.path.join(config.TS_DIR, fname) for fname in os.path.listdir(config.TS_DIR) if os.path.isfile(os.path.join(config.TS_DIR, fname))]
    clusters= cluster_anomalies(paths, 5)
    
    # now write each cluster to separate directory in cluster_dir
    for index, cluster in enumerate(clusters):
        curr_dir= os.path.join(cluster_dir, str(index))
        os.mkdir(curr_dir)
        print len(cluster)
        for ts_index in cluster:
            shutil.copy(paths[ts_index], curr_dir)            
'''


    


     


    


'''
if __name__=='__main__':            #DEPRECATED: due to bucketize
    # read all timeseries in path 
    path= os.path.join(os.getcwd(), sys.argv[1])
    plotsdir = os.path.join(os.getcwd(), sys.argv[2])
    outdir= os.path.join(os.getcwd(), sys.argv[3])


    # series_data is list((name, list(time, value))). need to pass only list(list(value))

    slist= list()
    nlist= list()
    index= 0
    for (name, series) in read_folder(path):
        print index
        slist.append(series)
        nlist.append(name)
        index+= 1
    print "computed slist, nlist"   
    bucketized_list= tsf.bucketize(slist, 100)

    print "computed bucketized_list"
        
    clusters= cluster(bucketized_list, 6, 20)
    cluster_names= map(lambda x: map(lambda y: nlist[y], x), clusters)

    if os.path.exists(outdir):
        shutil.rmtree(outdir)

    os.makedirs(outdir)

    for i in range(len(cluster_names)):
        dirname= os.path.join(outdir, str(i))
        os.makedirs(dirname)

    index= 0
    for cname in cluster_names:
        print index, len(cname)
        for name in cname:
            shutil.copy(os.path.join(plotsdir, name + ".png"), os.path.join(outdir, str(index)))
        index += 1
'''
