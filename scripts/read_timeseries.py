# read_timeseries- takes path of timeseries file and returns a list of (time, value) tuples 
# read_ts_iter- takes path of timeseries file and returns an iterator containing (time, value) tuples
import os
import sys
import pprint

class read_ts_iter:
    def __init__(self, path):
        self.fobj= open(path)
        print path
    
    def __iter__(self):
        return self
    
    def next(self):
        strvalues= self.fobj.next().split()
        return (float(strvalues[0]), float(strvalues[1]))

def read_timeseries(path):  # returns a list of (time, value) tuples
    ts_file= open(path) 
    timeseries= list()
    for line in ts_file:
        strvalues= line.strip().split()
        timeseries.append((float(strvalues[0]), float(strvalues[1])))
    # assume timeseries is sorted   
    ts_file.close()
    return timeseries

def read_lists(path):        # reads conventional timeseries file, and returns two lists- times, values
    ts_file= open(path) 
    times= list()
    values= list()
    for line in ts_file:
        strvalues= line.strip().split()
        times.append(float(strvalues[0]))
        values.append(float(strvalues[1]))
    ts_file.close()
    return times, values

        
if __name__== "__main__":
    '''
        # construct path
        pwd= os.getcwd()
        path= os.path.join(pwd, sys.argv[1])
        # read timeseries
        timeseries= read_timeseries(path)
        print timeseries

        # try iterator
        for (time, value) in read_ts_iter(path):
            print time, value
    '''
    pwd= os.getcwd()
    path= os.path.join(pwd, sys.argv[1])
    json_obj= read_json(path)
    pprint.pprint(json_obj)
