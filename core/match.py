import os, sys, json, pprint, math

if __name__=='__main__':
    sys.path.insert(0, "..")

import gateway 
from anomalies import aggregate, distance, max_anomalies, anomalies_to_weights, anomaly_weight_overlap, arrange_anomalies, anomalies_to_expweights
from server import config

#methods= ["naive"]
algorithms= ["naive", "hmm"]
features= [None, "mean", "var", "deviance"] # add slope?
window_sizes= [15, 30]


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
        anomaly_list.append(gateway.get_anomalies(path, algo, feature, window_size= w_size, percent= 10, mul_dev= 1.5))
    final_anomalies, weights= aggregate(anomaly_list, ratio)
    return final_anomalies 


def optimize_timeseries(path, mul_dev= 3, percent= 0.5, alpha = 0.7, top= None):      # returns anomalies sorted by weights and not time
    anomaly_dict= dict()
    anomaly_list= list()
    for algo in gateway.algo_iter(methods= ["naive"]):
        # TODO: replace with my_dict
        anomaly_list.append(gateway.get_anomalies(path, algo[0], algo[1], percent= percent, mul_dev= mul_dev, window_size= algo[2]))
        anomaly_dict[algo]= anomaly_list[-1]

    #final_anomalies= aggregate(anomaly_list)
    weights= anomalies_to_expweights(anomaly_list)
    max_overlap= -1
    for algo in gateway.algo_iter(methods= ["naive"]):
        # overlap penalized exponentially wrt length of anomaly list
        try:
            overlap= anomaly_weight_overlap(anomaly_dict[algo], weights)/math.exp(alpha * len(anomaly_dict[algo]))
        except OverflowError:
            overlap= 0
        #print algo, overlap
        if max_overlap < overlap:
            max_overlap= overlap
            max_algo= algo
    print "max algo= ", max_algo 
    #arranged_anomalies= arrange_anomalies(anomaly_dict[max_algo], weights)
    #print arranged_anomalies, len(arranged_anomalies)
    #if top==None:
    #    top= len(arranged_anomalies)
    #return arranged_anomalies[:top], max_algo
    return anomaly_dict[max_algo], max_algo


'''
def find_optimal_algo(anomaly_dict, final_anomalies):   # given the dict of anomalies, and the final list of anomalies, returns optimal algo, feature and window_size
    min_algo= (methods[0], features[0], window_sizes[0])
    min_dist= distance(final_anomalies, anomaly_dict[min_algo[0]][min_algo[1]][min_algo[2]])
    for algo, feature, window_size in algo_iter():
        curr_dist= distance(final_anomalies, anomaly_dict[algo][feature][window_size])
        print curr_dist
        if  curr_dist < min_dist:
            min_dist= curr_dist
            min_algo= (algo, feature, window_size)
    return min_algo
'''

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
        
if __name__=='__main__':
    print len(optimize_timeseries(sys.argv[1])[0])
    

'''
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

'''

