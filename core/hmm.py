import os, shutil
import sys
import numpy, scipy
import math
from math import log
import core.cluster as cluster
from scripts.read_timeseries import read_timeseries, read_lists
from scripts.ts_functions import bucketize
from core.anomalies import min_anomalies
from core.anomalies import index_to_interval
#from scripts.features import create_window_features

def emission_prob(value, cluster_mean, cluster_var):
    # find log(P(value | state))
    if cluster_var==0 and (value-cluster_mean)==0:
        return 0    # log(1)
    elif cluster_var==0:
        return -999999  # log(0)
    else:
        try:
            return - 0.5 * (log(2) + log(math.pi) + log(cluster_var)) - float(math.pow((value - cluster_mean), 2))/(2*cluster_var) 
        except ValueError:
            print "ValueError in emission_prob: ", value, cluster_mean, cluster_var

def logsumexp(array):
    lse= -float("inf")
    for number in array:
        lse= numpy.logaddexp(lse, number)
    return lse

def hmm_init(values, n_states, n_iter):     # for now just assign hard states. later run EM to assign soft states.
    # divide points into n_states clusters
    clusters= cluster.cluster(values, n_states, n_iter)
    # remove zero clusters
    clusters= [c for c in clusters if len(c) > 0]
    n_states= len(clusters)

    # compute mean and variance of each cluster
    n_pts= [0]*n_states
    sum_val= [0]*n_states
    sum_sqr= [0]*n_states

    for index, c in enumerate(clusters):
        n_pts[index]= len(c)
        sum_val[index]= sum(map(lambda x: values[x], c))
        sum_sqr[index]= sum(map(lambda x: values[x]*values[x], c))
        
    # compute state transition probabilities
    A= [[1]*n_states for i in range(0, n_states)]   # one added for laplace smoothing
    for i in range(0, len(values)-1):
        A[cluster.find_cluster(clusters, i)][cluster.find_cluster(clusters, i+1)]+= 1
    return A, n_pts, sum_val, sum_sqr


def hmm_add(value, A, n_pts, sum_val, sum_sqr, prev_state_prob):
    # returns updated A, cluster_means, cluster_vars, current_state_probs
    # A contains un normalized sum of P(s(t-1)= i, s(t)= j | O(t)) for all i, j over all time t. NOT in logspace
    # prev_state_logprob contains log of P(s(t-1)= i,  O(t-1)), where O(t-1) is o(1), ... o(t-1)
    # n_pts[i] contains sum(P(s(t)= i | O(t))) over all t
    # sum_val[i] contains sum(o(t) * P(s(t)=i | O(t))) over all t
    # sum_sqr[i] contains sum(o(t) * o(t) * P(s(t)=i | O(t))) over all t

    # calculate P(o(t) | s(t)=i) for every i
    n_states= len(n_pts)
    eprob= [0]*n_states
    #print sum_val, value
    for state in range(0, n_states):
        mean= sum_val[state]/n_pts[state]
        variance= max(sum_sqr[state]/n_pts[state] - math.pow(mean, 2), 0)
        eprob[state]= emission_prob(value, mean , variance)
    
    
    # now for every j s.t. s(t)= j, compute log of P(o(t) | s(t)= j) * sum_over_i(P(s(t)= j | s(t-1)= i) * P(O(t-1), s(t-1)= i))
    # P(o(t) | s(t)=j) is exp of eprob[j]
    # P(s(t)=j | s(t-1)=i) is A[j][i]
    # P(O(t-1), s(t-1)= i) is exp of prev_state_logprob[i]

    curr_state_probs= [0]*n_states
    # find normalized A
    norm_A= [[float(0)]*n_states for i in range(0, n_states)]
    for row in range(0, n_states):
        sum_row= sum(A[row])
        for column in range(0, n_states):
            norm_A[row][column]= float(A[row][column])/sum_row

    for curr_state in range(0, n_states):
        # need to use loglikelihoods and logsumexp to avoid underflow
        probs= [0]*n_states
        for prev_state in range(0, n_states):
            probs[prev_state]= prev_state_prob[prev_state] + log(norm_A[prev_state][curr_state])
        sum_probs= logsumexp(probs)
        curr_state_probs[curr_state]= sum_probs + eprob[curr_state]
    
    # now update A 
    # to add to A: First compute eta(i, j)= P(state(t-1)= i, state(t)= j , O(t))
    eta=[[0]*n_states for i in range(0, n_states)]
    # normalizer is P(O(t))- just sum over all curr_state_probs
    normalizer= logsumexp(curr_state_probs)

    for prev_state in range(0, n_states):
        for curr_state in range(0, n_states):
            eta[prev_state][curr_state]= prev_state_prob[prev_state] + log(norm_A[prev_state][curr_state]) + eprob[curr_state] - normalizer
    # add eta into A
    for prev_state in range(0, n_states):
        for curr_state in range(0, n_states):
            A[prev_state][curr_state]+= math.exp(eta[prev_state][curr_state])

    # update other three metrics
    # compute P(s(t)= i | O(t))- curr_state_prob divided by normalizer

    for state in range(0, n_states):
        prob= math.exp(curr_state_probs[state] - normalizer)

        n_pts[state]+= prob
        sum_val[state]+= prob * value
        sum_sqr[state]+= prob * value * value

    return curr_state_probs, A, n_pts, sum_val, sum_sqr, normalizer


def get_likelihoods(series, n_states):      # series is a list of just values- misnomer
    n_iter= 40  # iterations for initial kmeans
    n_q= 3      # number of states for which likelihood to be calculated
    # construct initial estimates from complete timeseries
    n_init= len(series)
    A, n_pts, sum_val, sum_sqr= hmm_init(series, n_states, n_iter)
    temp_n_states= len(n_pts)
    state_prob= [log(float(1)/temp_n_states)]*temp_n_states
    queue= list()
    likelihoods= list()
    curr_prob= 0

    for i, value in enumerate(series):
        state_prob, A, n_pts, sum_val, sum_sqr, obs_prob= hmm_add(value, A, n_pts, sum_val, sum_sqr, state_prob)
        
        if obs_prob < -1e250:
            # normalize state_prob
            print "before: ", obs_prob, state_prob
            for state in range(0, temp_n_clusters):
                state_prob[state]-= obs_prob
            print "after: ", state_prob

        queue.insert(0, obs_prob)
        if len(queue) > n_q:
            curr_prob= obs_prob - queue.pop()
        likelihoods.append(curr_prob)
    return likelihoods

def likelihoods_to_anomalies(times, values, ratio):             # DEPRECATED
    # does not support bucketized values
    indices= sorted(range(len(values)), key= lambda x: values[x])
    indices= sorted(indices[:int(len(indices) * ratio)])
    return index_to_interval(indices, times)

def get_anomalies(path, n_states, ratio, feature_func= None, window_size= 15):       # DEPRECATED
    times, values= read_lists(path)
    #featurelist= create_window_features(values, window_size, feature_func)  # add slope functionality
    factor= 15
    new_series= bucketize(times, values, len(values)/factor)
    likelihoods= get_likelihoods(new_series, n_states)
    #likelihoods= get_likelihoods(featurelist, n_states)
    return likelihoods_to_anomalies(times, likelihoods, ratio, factor)

def get_anomalies_from_series(times, values, n_states, ratio):  # DEPRECATED
    factor= 50
    new_values= bucketize(times, values, len(values)/factor)
    likelihoods= get_likelihoods(new_values, n_states) 
    return likelihoods_to_anomalies(times, likelihoods, ratio, factor)
    
if __name__=='__main__':
    path= os.path.join(os.getcwd(), sys.argv[1])
    n_clusters= int(sys.argv[2])
    anomalies= get_anomalies(path, n_clusters, 0.1)
    print anomalies
    print len(anomalies)


