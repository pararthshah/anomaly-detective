import os, sys, json, pprint
import gateway 
from anomalies import aggregate, distance, max_anomalies
from server import config

#algorithms= ["naive"]
algorithms= ["naive", "hmm"]
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

def machine_majority_vote(path, ratio):    # reads file containing machine weights and returns anomalies
    # TODO: hacky way, improve
    ts_name= os.path.basename(path)
    dir_name= os.path.dirname(path)
    machine_name= ts_name.split("-")[0]
    weights_path= os.path.join(dir_name, "..", "machine_weights", machine_name)
    weights= [int(line.strip()) for line in open(weights_path, 'r')]
    anomalies= max_anomalies(range(0, len(weights)), weights, ratio)
    return anomalies

def ts_majority_vote(path, ratio= 0.005):
    anomaly_list= list()
    for algo, feature, w_size in algo_iter():
        anomaly_list.append(gateway.get_anomalies(path, algo, feature, window_size= w_size, percent= 3, mul_dev= 2.5))
    print anomaly_list
    final_anomalies, weights= aggregate(anomaly_list, ratio)
    print final_anomalies
    return final_anomalies 


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
            
        anomaly_list.append(gateway.get_anomalies(path, algo, feature, percent=0.5, mul_dev= 3, window_size= w_size))
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
                
            anomaly_list.append(gateway.get_anomalies(path, algo, feature, percent=2, mul_dev= 3, window_size= w_size))
            print len(anomaly_list[-1])
            anomaly_dict[path][algo][feature][w_size]= anomaly_list[-1]

    final_anomalies, weights= aggregate(anomaly_list, ratio= 0.01)
    min_algo= list()
    anomalies= list()
    for path in paths:
        min_algo.append(find_optimal_algo(anomaly_dict[path], final_anomalies))
        a= min_algo[-1]
        anomalies.append(anomaly_dict[path][a[0]][a[1]][a[2]])
    return min_algo, anomalies, final_anomalies, weights
        

if __name__=="__main__":
    sys.path.insert(0, "..")
    machine_name= sys.argv[1]
    imp_file= open("../data/important.json", 'r')
    names= json.load(imp_file)
    imp_file.close()
    # create list of paths to all timeseries for machine_name
    paths= list()
    for ts in names[machine_name]:
        path= os.path.join(os.getcwd(), config.TS_DIR, str(machine_name) + "-" + str(ts) + ".data")
        paths.append(path)

    min_algo, anomalies, final_anomalies, weights= optimize_machine(paths)
    for i, path in enumerate(paths):
        pprint.pprint(path)
        pprint.pprint(min_algo[i])
    #pprint.pprint(anomalies)
    pprint.pprint(final_anomalies)
    # write machine weights in a file
    if not os.path.exists(config.MACHINE_WTS_DIR):
        os.mkdir(config.MACHINE_WTS_DIR)

    fout= open(os.path.join(config.MACHINE_WTS_DIR, machine_name), 'w')
    for weight in weights:
        fout.write("%d\n" % weight)
    fout.close()


