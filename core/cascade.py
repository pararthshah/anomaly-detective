from scipy.stats import ks_2samp
import numpy as np
import datetime
import math

def getDate(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%m-%d %H:%M')

def compute_ks1(values, w11, w12, w21, w22):
    w1 = values[w11:w12]
    w2 = values[w21:w22]
    m1 = np.mean(w1)
    m2 = np.mean(w2)
    x = np.asarray(map(lambda x: x, w1))
    y = np.asarray(map(lambda x: x, w2))
    return ks_2samp(x, y)

def compute_ks(values, c1, c2):
    return compute_ks1(values, c1[0], c1[1], c2[0], c2[1])

def combine_candidates(candidates):
    curr_beg = candidates[0][0]
    curr_end = candidates[0][1]
    results = []
    for c in candidates[1:]:
        if c[0] <= curr_end+10:
            curr_end = max(curr_end,c[1])
        else:
            results.append([curr_beg, curr_end])
            curr_beg = c[0]
            curr_end = c[1]
    results.append([curr_beg, curr_end])
    print "No. anomalies=", len(results)
    return results

def combine_likelihoods(times, candidates, threshold):
    results = []
    if len(candidates) == 0:
        return results
    likelihoods = [0.0 for i in range(len(times))]
    for c in candidates:
        for i in range(c[0],c[1]):
            likelihoods[i] += c[2]
    curr_beg = -1
    curr_end = -1
    flag = 0
    for i in range(len(times)):
        if likelihoods[i] > threshold:
            if flag == 0:
                curr_beg = i
                curr_end = i
                flag = 1
            else:
                curr_end = i
        else:
            if curr_beg > -1:
                results.append([curr_beg, curr_end])
            flag = 0
    if curr_beg > -1:
        results.append([curr_beg, curr_end])
    print "No. anomalies=", len(results)
    # return results

def compute_anomalies(times, values, base=512, levels=1):
    num_points = len(times)
    window_size = base
    candidates = []
    for l in range(levels):
        jump_size = window_size/2
        for index in range(0, num_points, jump_size):
            if index+window_size > num_points or index-window_size < 0:
                continue
            c_win = (index, index+window_size)
            p_win = (max(index-4*window_size, 0), index)
            curr_ks = compute_ks(values, c_win, p_win)[1]
            curr_val = 10000
            if curr_ks != 0.0:
                curr_val = -1*math.log10(curr_ks)
            if curr_val >= 5:
                candidates.append((index, index+window_size, curr_val, l))
        window_size *= 2
    print len(candidates)
    print "\n".join(map(lambda x: getDate(times[x[0]]) + ", " + getDate(times[x[1]]) + ": " + str(x[2]) + " " + str(x[3]), candidates))
    #return combine_likelihoods(times, candidates, 3*levels)

def compute_likelihoods(times, values, base=512, levels=1):
    num_points = len(times)
    window_size = base
    jump_size = window_size/2
    likelihoods = []
    for index in range(0, num_points, jump_size):
        if index+window_size > num_points or index-window_size < 0:
            continue
        c_win = (index, index+window_size)
        p_win = (max(index-4*window_size, 0), index)
        curr_ks = compute_ks(values, c_win, p_win)[1]
        if curr_ks == 0.0:
            curr_ks = 100
        else:
            curr_ks = -1*math.log10(curr_ks)
        for i in range(index,index+window_size):
            likelihoods.append([times[i], curr_ks])
    return likelihoods

def compute_anomalies1(times, values, base=512, levels=1):
    num_points = len(times)
    window_size = base
    jump_size = window_size/2
    prev_ks = []
    candidates = []
    for index in range(0, num_points, jump_size):
        if index+window_size > num_points or index-window_size < 0:
            continue
        c_win = (index, index+window_size)
        p_win = (max(index-4*window_size, 0), index)
        curr_ks = compute_ks(values, c_win, p_win)
        if curr_ks[1] == 0.0 or -1*math.log10(curr_ks[1]) > 10:
            candidates.append([times[index], times[index+window_size]])
        # if len(prev_ks) > 0:
        #     prev_mean = np.mean(prev_ks)
        #     prev_sd = np.std(prev_ks)
        #     if abs(curr_ks - prev_mean) > 3*prev_sd:
        #         candidates.append((times[index], times[index+window_size], curr_ks))
        # prev_ks.insert(0,curr_ks)
        # if len(prev_ks) > 4:
        #     prev_ks.pop()
    anomalies = combine_candidates(candidates)
    return anomalies
    #return "\n".join(map(lambda x: getDate(x[0]) + ", " + getDate(x[1]), anomalies))

    # buckets = []
    # index = 0
    # while index+window_size < num_points:
    #     buckets.append((times[index], times[index+window_size], np.asarray(values[index:index+window_size])))
    #     index += jump_size
    # ks_values = []
    # for i in range(len(buckets)):
    #     curr_values = []
    #     for j in range(i-1,i-5,-1):
    #         if j < 0:
    #             continue
    #         curr_values.append(ks_2samp(buckets[i][2], buckets[j][2])[0])
    #     ks_values.append((buckets[i][0], buckets[i][1], curr_values))
    # #candidates = sorted(map(lambda x: (x[0], x[1], sum(x[2])), ks_values),key=lambda x:x[2],reverse=True)[:20]
    # return "\n".join(map(lambda x: getDate(x[0]) + ", " + getDate(x[1]) + ": " + str(sum(x[2])), ks_values))
    # anomalies = sorted(map(lambda x: [x[0], x[1]], candidates))
    # return anomalies



