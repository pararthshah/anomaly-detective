import os, shutil
import sys
import numpy, scipy
import math
from math import log
from cluster import cluster
from cluster import find_cluster
from scripts.read_timeseries import read_timeseries
from scripts.ts_functions import bucketize

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
    clusters= cluster(values, n_states, n_iter)
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
        A[find_cluster(clusters, i)][find_cluster(clusters, i+1)]+= 1
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
    
    
    # now for every j s.t. s(t)= j, compute log of P(o(t) | s(t)= j) * sum_over_i(P(s(t)= j | s(t-1)= i) * P(O(t-1), s(t-1)= j))
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


def get_likelihoods(series, n_states):
    n_iter= 10  # iterations for initial kmeans
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


def get_anomalies(path, n_states, ratio):
    series= read_timeseries(path)
    print "length of series= ", series[-1][0]
    factor= 15
    new_series= bucketize(series, len(series)/15)
    likelihoods= get_likelihoods(new_series, n_states)

    # now find the mean and standard deviation of the likelihoods and assume that they are gaussian to find lowest percent of likelihoods
    ll_sorted= sorted(enumerate(likelihoods), key= lambda x: x[1])
    ll_index= map(lambda x:x[0], ll_sorted)
    ll_index= sorted(ll_index[:int(len(ll_index) * ratio)])

    anomalies= list()
    index= 0 
    while index < len(ll_index):
        start_time= series[ll_index[index]*15][0]
        while index < len(ll_index)-1 and ll_index[index + 1] == ll_index[index] + 1:
            index+= 1
        end_time= series[ll_index[index]*15 + 1][0]
        anomalies.append((start_time, end_time))
        index+= 1
    return anomalies


if __name__=='__main__':
    
    path= os.path.join(os.getcwd(), sys.argv[1])
    n_clusters= int(sys.argv[2])
    anomalies= get_anomalies(path, n_clusters, 0.1)
    print anomalies
    print len(anomalies)


'''
if __name__=="__main__":
    # argument 1- directory containing timeseries data
    # argument 2- directory that should contain logprob data
    # argument 3- number of clusters
    n_clusters= int(sys.argv[3])
    path= os.path.join(os.getcwd(), sys.argv[1])
    outdir= os.path.join(os.getcwd(), sys.argv[2])
#   if os.path.exists(outdir):
#       shutil.rmtree(outdir)
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    n_q= 3  # find probability of 3 consequitive observations given the rest of the data
    file_no= 0
    for (name, series) in read_folder(path):
        print file_no, len(series)
        file_no+= 1
        outpath= os.path.join(outdir, name)
        if os.path.isfile(outpath):
            print "file found!"
            continue
        queue= list()
        curr_prob= 0
        n_init= min(500, int(len(series)*0.3))
        fout= open(outpath, 'w')
        
        A, n_pts, sum_val, sum_sqr= hmm_init(map(lambda x:x[1], series[0:n_init]), n_clusters)
        temp_n_clusters= len(n_pts)

        #print A, n_pts, sum_val, sum_sqr
        for i in range(0, n_init):
            fout.write("%f\t%f\n"% (series[i][0], curr_prob))

        state_prob= [log(float(1)/temp_n_clusters)]*temp_n_clusters

        for time, value in series[n_init:]:
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
#           print curr_prob
            fout.write("%f\t%f\n"% (time, curr_prob))
        fout.close()
''' 

'''
if __name__=="__main__":
    a= [1.0, 1.1, 1.2, 1.3, 6.0, 6.1, 6.2, 6.3] 
    A, n_pts, sum_val, sum_sqr= hmm_init(a, 2)
#   print A, n_pts, sum_val, sum_sqr    
    state_prob= [0.5, 0.5]

    b= [1.3, 6.0, 1.4, 6.1, 1.2, 6.2, 1.1]

    for value in b:
        state_prob, A, n_pts, sum_val, sum_sqr= hmm_add(value, A, n_pts, sum_val, sum_sqr, state_prob)
        prob_obs= logsumexp(state_prob)
        print map(lambda x: x- prob_obs, state_prob)
'''
