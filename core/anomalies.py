def aggregate(anomaly_list, ratio= 0.0005):   # accepts list of anomalies
    # TODO: try exponential taper off, instead of discrete one
    max_time= 0
    for anomalies in anomaly_list:
        if len(anomalies) > 0 and anomalies[-1][1] > max_time:
            max_time= anomalies[-1][1]

    weights= [0]*int(max_time)   # hope that times start from 0

    for anomalies in anomaly_list:
        for start, end in anomalies:
            for i in range(int(start), int(end)):
                weights[i]+= 1
    # now find most significant weights
    return max_anomalies(range(0, len(weights)), weights, ratio), weights

def max_anomalies(times, values, ratio):   # finds highest weights and returns them as anomalies- similar to likelihoods_to_anomalies in hmm.py
    indices= sorted(range(len(values)), key= lambda x: values[x], reverse=True)
    indices= sorted(indices[:int(len(indices) * ratio)])
    return index_to_interval(indices, times)

def min_anomalies(times, values, ratio):   # finds highest weights and returns them as anomalies- similar to likelihoods_to_anomalies in hmm.py
    indices= sorted(range(len(values)), key= lambda x: values[x])
    indices= sorted(indices[:int(len(indices) * ratio)])
    return index_to_interval(indices, times)

def index_to_interval(indices, times):     # converts a list of flagged indices to anomaly intervals
    anomalies= list()
    i= 0
    while i < len(indices):
        start_time= times[indices[i]]
        while i < len(indices)-1 and indices[i + 1] == indices[i] + 1:
            i+= 1
        end_time= times[min(len(times)-1, indices[i] + 1)]
        anomalies.append((start_time, end_time))
        i+= 1
    return anomalies

def distance(a1, a2):   # finds the "edit distance" between two anomalies- jaccard distance
    if len(a1)== 0 or len(a2)== 0:
        return float("inf")
    max_time= max(a1[-1][1], a2[-1][1])
    a1_counter= 0
    a2_counter= 0
    union= 0

    while a1_counter < len(a1) and a2_counter < len(a2):
        union+= overlap(a1[a1_counter], a2[a2_counter])
        if a1[a1_counter][1] > a2[a2_counter][1]:
            a2_counter+= 1
        else:
            a1_counter+= 1

    return float(union)/(total_time(a1)*total_time(a2))
    
def overlap(int1, int2):    # finds time overlap between two intervals
    val= min(int1[1], int2[1]) - max(int1[0], int2[0])
    if val>0:
        return val
    else:
        return 0

def total_time(anomaly):    # finds total anomalous time in an anomaly
    t= 0
    for interval in anomaly:
        t+= (interval[1]-interval[0]) 
    return t
    
        
    
