import sys, os, pprint
if __name__=='__main__':
    sys.path.insert(0, "..")
import server.config as config
from scripts.read_folder import read_folder_lists
import core.gateway as gateway
from core.anomalies import anomalies_to_onesided_expweights, anomaly_weight_overlap


def find_corr_matrix(dataset):
    paths= config.paths(dataset)
    anomaly_dict= dict() 
    for index, path in enumerate([os.path.join(paths.TS_DIR, f) for f in os.listdir(paths.TS_DIR)]):
        anomaly_dict[path]= gateway.get_anomalies(path, "combined_hmm", None, percent= 0.5)
        #print(path)
        print index
        print(anomaly_dict[path])

    paths= list()
    cor_mat= list()
    for i, path in enumerate(anomaly_dict):
        paths.append(path)
        cor_mat.append(list())
        weights= anomalies_to_onesided_expweights(anomaly_dict[path])
        for j, otherpath in enumerate(anomaly_dict):
            cor_mat[i].append(anomaly_weight_overlap(anomaly_dict[otherpath], weights))

    return paths, cor_mat

if __name__=='__main__':
    paths, cor_mat= find_corr_matrix(sys.argv[1])
    pprint.pprint(cor_mat)

            
    