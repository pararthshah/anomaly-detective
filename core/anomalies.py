from naive import index_to_interval

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
    anomaly_indices= find_highest(weights, ratio)
    anomalies= index_to_interval(anomaly_indices, range(0, int(max_time)))
    return anomalies

def find_highest(weights, ratio):
    indices= sorted(range(len(weights)), key= lambda x: weights[x], reverse=True)
    indices= sorted(indices[:int(len(indices) * ratio)])
    return indices

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
    
        
    
