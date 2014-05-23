
def fit_ts(times, values, timevalues): # fits the timeseries into the given time values, returns only list(values), NOT list((time, value))
    if len(times) != len(values):
        print len(times), len(values)
        raise Exception("Error in fit_ts")
    new_values= list()
    ts_index= 0

    # start from time timevalues[0], ignore previous values
    while times[ts_index] < timevalues[0]:
        ts_index+= 1

    for index, time in enumerate(timevalues):
        n_values= 0
        sum_values= 0
        if(index== len(timevalues)-1):          # if this is the last bucket, take average of all remaining values in timeseries
            sum_values= sum(values[ts_index:-1])
            n_values= len(values) - ts_index
        else:                                   # otherwise take average of values till start of next bucket
            while times[ts_index] < timevalues[index+1]:
                n_values+= 1
                sum_values+= values[ts_index]
                ts_index+= 1
        if (n_values > 0):
            new_values.append(sum_values/n_values)
        elif(len(new_series)>0):
            new_values.append(new_series[-1])   # append the last value
        else:
            new_values.append( 0)               # if no prev. value available append 0
    return new_values
            

def find_common_timeinterval(timelists):    # returns a time interval common to all ts in slist
    mintime= max([times[0] for times in timelists])
    maxtime= min([times[-1] for times in timelists])
    return (mintime, maxtime)


def combine(timelists, valuelists, n_buckets):        # trims one or a list of timeseries so that all contain common times and then bucketizes them
    if len(timelists) != len(valuelists):
        raise Exception("Non matching lengths in ts_functions.combine")

    (mintime, maxtime)= find_common_timeinterval(timelists)

    x= int((maxtime-mintime)/n_buckets)
    timevalues= range(int(mintime), int(maxtime), int((maxtime-mintime)/n_buckets))
    if type(timelists[0]) is list:
        bucketlist= [fit_ts(times, values, timevalues) for times, values in zip(timelists, valuelists)]
    else:
        bucketlist= fit_ts(timelists, valuelists, timevalues)
    return timevalues, bucketlist

def bucketize(times, values, bucket_size):
    mintime= times[0]
    maxtime= times[1]
    blist= list()
    for start, end in bucket_iter(len(values), bucket_size):
        bucket= values[start:end]
        blist.append(sum(bucket)/len(bucket))
    return blist

def de_bucketize(times, values, bucket_size):
    # de bucketizes values to match length of times
    counter= 0
    new_list= list()
    for start, end in bucket_iter(len(times), bucket_size): 
        new_list.extend([values[counter] for x in range(start, end)])
        counter+=1
    if len(new_list) != len(times):
        print len(new_list), len(times)
        raise Exception("Error in de_bucketize")
    else:
        return new_list


def bucket_start(bucket_number, bucket_size):   # inclusive
    return bucket_number * (2*bucket_size + 1)

def bucket_end(bucket_number, bucket_size):     # exclusive!
    return (bucket_number + 1)*(2*bucket_size+1)

def bucket_mid(bucket_number, bucket_size):
    return bucket_start(bucket_number, bucket_size) + bucket_size

class window_iter():    # iterates over windows of value list
    def __init__(self, values, window_size):
        self.values= values
        self.window_size= window_size
        self.counter= -1     # counter holds the index of start of window

    def __iter__(self):
        return self

    def next(self):
        self.counter+= 1
        if self.counter + self.window_size > len(self.values):
            raise StopIteration
        else:
            return self.values[self.counter:self.counter + self.window_size] 
    
class bucket_iter():
    # iterator which returns (start, end) indices for buckets over list of length n
    def __init__(self, n, bucket_size):    # actual bucket_size is 2*()+1
        self.n= n
        self.bucket_size= bucket_size
        self.counter= -1

    def __iter__(self):
        return self

    def next(self):
        self.counter+= 1
        if bucket_start(self.counter, self.bucket_size) >= self.n:
            raise StopIteration
        else: 
            return bucket_start(self.counter, self.bucket_size), min(bucket_end(self.counter, self.bucket_size), self.n)
            #return values[bucket_start(self.counter, self.bucket_size):bucket_end(self.counter, self.bucket_size)]
            
