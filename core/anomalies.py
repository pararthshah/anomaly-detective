import math

def anomalies_to_weights(anomaly_list):     # UNUSED- anomalies_to_expweights preferred
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
    return weights

def anomalies_to_expweights(anomaly_list, alpha= 500):
    # do an efficient exponential taper off
    cutoffs= [1, 0.7, 0.5, 0.2, 0.1]
    # find cutoff_intervals
    intervals= list()
    for cutoff in cutoffs:
        intervals.append(-int(math.log(cutoff) * alpha))
    max_time= 0
    for anomalies in anomaly_list:
        if len(anomalies) > 0 and anomalies[-1][1] > max_time:
            max_time= anomalies[-1][1]
    max_time= int(max_time)
    weights= [0]*max_time   # hope that times start from 0
    
    for anomalies in anomaly_list:
        for start, end in anomalies:
            for cutoff, interval in zip(cutoffs, intervals):
                for i in range(max(0, int(start) - interval), min(max_time, int(end) + interval)):
                    weights[i]+= cutoff
    return weights

def anomalies_to_onesided_expweights(anomalies, alpha= 1000):   # accepts only a single anomaly list, not a list of lists
    cutoffs= [1, 0.7, 0.5, 0.2, 0.1]
    # find cutoff_intervals
    intervals= list()
    for cutoff in cutoffs:
        intervals.append(-int(math.log(cutoff) * alpha))
    max_time= int(anomalies[-1][1])
    weights= [0]*max_time   # hope that times start from 0
        
    for start, end in anomalies:
        for cutoff, interval in zip(cutoffs, intervals):
            for i in range(int(end), min(max_time, int(end) + interval)):
                weights[i]+= cutoff
    return weights

def anomaly_weight_overlap(anomalies, weights): # not normalized!
    if len(anomalies)==0:
        return 0            # how to avoid penalizing for ts without anomalies?
    overlap= 0
    for anomaly in anomalies:
        if anomaly[0] < len(weights):
            overlap+= sum(weights[min(int(anomaly[0]), len(weights)-1) : min(int(anomaly[1]), len(weights))])
        else:
            break
    return float(overlap)

def arrange_anomalies(anomalies, weights):  # arranges anomalies by amount of overlap (or should it be average overlap?)
    overlap= list()
    for anomaly in anomalies:
        if anomaly[0] < len(weights):
            overlap.append(sum(weights[max(int(anomaly[0]), len(weights)-1) : max(int(anomaly[1]), len(weights))]))
        else:
            overlap.append(0)
    return [y for (x, y) in sorted(zip(overlap, anomalies))]
            
def aggregate(anomaly_list, ratio= 0.0005):   # accepts list of anomalies
    weights= anomalies_to_weights(anomaly_list)
    # now find most significant weights
    return max_anomalies(range(0, len(weights)), weights, ratio), weights

def max_anomalies(times, values, ratio= 0.0005):   # finds highest weights and returns them as anomalies- similar to likelihoods_to_anomalies in hmm.py
    indices= sorted(range(len(values)), key= lambda x: values[x], reverse=True)
    indices= sorted(indices[:int(len(indices) * ratio)])
    return index_to_interval(indices, times)

def min_anomalies(times, values, ratio= 0.0005):   # finds highest weights and returns them as anomalies- similar to likelihoods_to_anomalies in hmm.py
    indices= sorted(range(len(values)), key= lambda x: values[x])
    indices= sorted(indices[:int(len(indices) * ratio)])
    return index_to_interval(indices, times)

def ordered_min_anomalies(times, values, ratio= 0.0005):
    indices= sorted(range(len(values)), key= lambda x: values[x])
    indices= sorted(indices[:int(len(indices) * ratio)])
    anomalies, time_indices= index_to_interval(indices, times, return_indices= True)
    # find endpoint indices of anomalies in the "times" array
    #print anomalies, time_indices
    ordered_anomaly_indices= sorted(range(0, len(anomalies)), key= lambda i: float(sum(values[time_indices[i][0]:time_indices[i][1]]))/(times[time_indices[i][1]]-times[time_indices[i][0]]))
    ordered_anomalies= [anomalies[i] for i in ordered_anomaly_indices]
    ordered_overlaps= sorted([float(sum(values[time_indices[i][0]:time_indices[i][1]]))/(times[time_indices[i][1]]-times[time_indices[i][0]]) for i in range(0, len(anomalies))])
    return ordered_anomalies, ordered_overlaps


def min_cutoff(anomalies, overlaps, percent= 10, initial_exempt= 3):    # cuts off the list of anomalies where the average overlap increases by percent
    i= initial_exempt
    prev_avg= float(sum(overlaps[:i]))/min(len(overlaps), i)
    for i in range(initial_exempt+1, len(overlaps)):
        curr_avg= float(sum(overlaps[:i]))/i
        if curr_avg > prev_avg * (1+percent/100):
            i= i-1
            break
    return anomalies[:i]
    #return anomalies


def index_to_interval(indices, times, return_indices= False):     # converts a list of flagged indices to anomaly intervals
    anomalies= list()
    time_indices= list()
    i= 0
    while i < len(indices):
        start_time= times[indices[i]]
        start_index= indices[i]
        while i < len(indices)-1 and indices[i + 1] == indices[i] + 1:
            i+= 1
        end_time= times[min(len(times)-1, indices[i] + 1)]
        end_index= min(len(times)-1, indices[i]+1)
        anomalies.append((start_time, end_time))
        time_indices.append((start_index, end_index))
        i+= 1
    if return_indices:
        return anomalies, time_indices
    else:
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
    
