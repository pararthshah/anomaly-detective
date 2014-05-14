import os, sys, json, pprint
from gateway import get_anomalies
from anomalies import aggregate, distance
from naive import index_to_interval

algorithms= ["naive"]
#algorithms= ["naive", "hmm"]
features= [None, "mean", "var", "deviance"] # add slope?
window_sizes= [15, 30]

class algo_iter:
    def __init__(self):    
        self.algo_list= [(x, y, z) for z in window_sizes for y in features for x in algorithms]
        self.counter= -1
    
    def __iter__(self):
        return self

    def next(self):
        self.counter+= 1
        if self.counter < len(self.algo_list):
            return self.algo_list[self.counter]
        else:
            raise StopIteration

def optimize_timeseries(path):
    anomaly_dict= dict()
    anomaly_list= list()
    for algo, feature, w_size in algo_iter():
        # TODO: replace with my_dict
        try:
            var= anomaly_dict[algo]
        except KeyError:
            anomaly_dict[algo]= dict()

        try:
            var= anomaly_dict[algo][feature]
        except KeyError:
            anomaly_dict[algo][feature]= dict()
            
        anomaly_list.append(get_anomalies(path, algo, feature, percent=0.5, mul_dev= 3, window_size= w_size))
        anomaly_dict[algo][feature][w_size]= anomaly_list[-1]

    final_anomalies= aggregate(anomaly_list)
    #return final_anomalies
    min_dist= distance(final_anomalies, anomaly_dict[algorithms[0]][features[0]][window_sizes[0]])  # do using algo_iter.get_init()
    print min_dist
    min_algo= find_optimal_algo(anomaly_dict, final_anomalies)
    return min_algo, anomaly_dict[min_algo[0]][min_algo[1]][min_algo[2]], final_anomalies


def find_optimal_algo(anomaly_dict, final_anomalies):   # given the dict of anomalies, and the final list of anomalies, returns optimal algo, feature and window_size
    min_algo= (algorithms[0], features[0], window_sizes[0])
    min_dist= distance(final_anomalies, anomaly_dict[min_algo[0]][min_algo[1]][min_algo[2]])
    for algo, feature, window_size in algo_iter():
        curr_dist= distance(final_anomalies, anomaly_dict[algo][feature][window_size])
        print curr_dist
        if  curr_dist < min_dist:
            min_dist= curr_dist
            min_algo= (algo, feature, window_size)
    return min_algo

def optimize_machine(paths):    # optimizes over all the timeseries provided in the path list
    # returns a list of algorithms and a list of corresponding anomalies
    anomaly_dict= dict()
    anomaly_list= list()
    index= 1
    for path in paths:
        anomaly_dict[path]= dict()
        print "finding anomaly for path no." + str(index), path
        index+= 1
        for algo, feature, w_size in algo_iter():
            # TODO: replace with my_dict
            try:
                var= anomaly_dict[path][algo]
            except KeyError:
                anomaly_dict[path][algo]= dict()

            try:
                var= anomaly_dict[path][algo][feature]
            except KeyError:
                anomaly_dict[path][algo][feature]= dict()
                
            anomaly_list.append(get_anomalies(path, algo, feature, percent=2, mul_dev= 2.5, window_size= w_size))
            print len(anomaly_list[-1])
            anomaly_dict[path][algo][feature][w_size]= anomaly_list[-1]

    final_anomalies= aggregate(anomaly_list)
    min_algo= list()
    anomalies= list()
    for path in paths:
        min_algo.append(find_optimal_algo(anomaly_dict[path], final_anomalies))
        a= min_algo[-1]
        anomalies.append(anomaly_dict[path][a[0]][a[1]][a[2]])
    return min_algo, anomalies, final_anomalies
        

if __name__=="__main__":
    #path= os.path.join(os.getcwd(), sys.argv[1])
    machine_name= sys.argv[1]
    imp_file= open("../data/important.json", 'r')
    names= json.load(imp_file)
    imp_file.close()
    # create list of paths to all timeseries for machine_name
    paths= list()
    for ts in names[machine_name]:
        path= os.path.join(os.getcwd(), sys.argv[2], str(machine_name) + "-" + str(ts) + ".data")
        paths.append(path)
    pprint.pprint(paths)
    min_algo, anomalies, final_anomalies= optimize_machine(paths)
    pprint.pprint(min_algo)
    #pprint.pprint(anomalies)
    pprint.pprint(final_anomalies)

def dummy():    # final_anomalies for the first machine
    anomalies= [(31085, 31090), (44405, 44410), (44425, 44430), (44435, 44444), (44445, 44645), (44670, 44676), (68308, 68310), (85020, 85025), (85095, 85105), (85115, 85130), (85135, 85155), (327225, 327230), (550340, 550350), (550365, 550375)]
    return anomalies

    
