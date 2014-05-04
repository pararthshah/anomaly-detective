import os, shutil
import sys
import random
import math
from scripts.read_folder import read_folder
import scripts.ts_functions as tsf

def cluster(slist, n_clusters, n_iter):	# slist should be a list(list(values)) or list(values)
	# implement in memory k means clustering for now
	n_lists= len(slist)

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
				dist= distance(centroid, series)
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
	
	
def distance(ts1, ts2):		# find distance between two timeseries
	if type(ts1) is list and type(ts2) is list:
		# normalize timeseries
		nts1= normalize(ts1)
		nts2= normalize(ts2)
		dist= 0	
		for (pt1, pt2) in zip(nts1, nts2):
			dist+= (pt1 - pt2)*(pt1 - pt2)
		return math.sqrt(dist)
	elif type(ts1) is float and type(ts2) is float:
		return math.sqrt(math.pow((ts1 - ts2), 2))
	else:
		print "error!"
		return -1

def normalize(ts):	# normalizes by dividing my max
	max_ts= max(ts)
	if(max_ts != 0):
		return map(lambda x:x/max_ts, ts)
	else:
		return ts
	

def find_centroid(cluster):	# for now simply finds the average of timeseries
	n_series= len(cluster)
	if type(cluster[0]) is list:
		avg_series= [0]*len(cluster[0])
		for series in cluster:
			for index, point in enumerate(series):
				avg_series[index]+= point
		avg_series= map(lambda x:x/n_series, avg_series)
		return avg_series

	elif type(cluster[0]) is float:
	 	return sum(cluster)/len(cluster)
	else:
		print "error!"
		return -1
	
def find_cluster(clusters, index):	# returns index in clusters which contains "index"
	for i, cluster in enumerate(clusters):
		if index in cluster:
			return i
	return -1
	
	
if __name__=='__main__':
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

