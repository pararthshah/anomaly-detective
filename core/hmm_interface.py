import pyRserve
import os, sys
from scripts.read_timeseries import read_timeseries
from scripts.ts_functions import bucketize
import server.config as config

def run_hmm(series, nStates):   
    conn= pyRserve.connect()
    srcpath= os.getcwd()    # assumes that hmm.r is in the same directory as this python file
    conn.eval('setwd("' + config.CORE_DIR + '")')
    conn.eval('source("hmm.r")')
    conn.eval('library("RHmm")')
    conn.r.sc= series
    conn.r.nStates= nStates
    streval= 'v <- run_hmm(sc, n_states= nStates )'
    conn.eval(streval)
    return conn.r.v

def get_anomalies(path, n_states, ratio):
    series= read_timeseries(path)
    factor= 10
    new_series= bucketize(series, len(series)/factor)
    v= run_hmm(new_series, n_states)
    v= map(lambda x: int(x), v)
    hist= get_histogram(v)      # return sorted histogram
    n_flagged= 0
    flagged_values= list()
    for index, value in enumerate(hist):
        if n_flagged < len(v) * ratio and index != len(hist)-1:
            #print n_flagged, len(v), ratio, len(v) * ratio, " done "
            n_flagged+= value
            flagged_values.append(index+1)


    # get intervals
    curr_flagged= 0
    intervals= list()
    for index, value in enumerate(v):
        if value in flagged_values and curr_flagged== 0:
            start_int= index*factor
            curr_flagged= 1
        if value not in flagged_values and curr_flagged== 1:
            intervals.append((start_int, index*factor))
            curr_flagged= 0
    if curr_flagged==1:
        intervals.append((start_int, min(index*factor, len(v)-1)))
    # convert intervals - indices to time values
    intervals= map(lambda (x, y):(series[x][0], series[y][0]), intervals)
    return intervals
                
def get_histogram(v):
    maxval= max(v)
    histogram= [0]*(maxval)
    for value in v:
        histogram[value-1]+= 1
    return sorted(histogram)

if __name__=="__main__":
    pwd= os.getcwd()
    path= os.path.join(pwd, sys.argv[1])
    #v= run_hmm(path, int(sys.argv[2]))
    intervals= get_anomalies(path, 10, 0.2)
    print intervals
    print len(intervals)

