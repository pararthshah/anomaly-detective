# functions useful for cluster.py

def fit_ts(ts, timevalues):	# fits the timeseries into the given time values, returns only list(values), NOT list((time, value))
	new_series= list()
	ts_index= 0

	# start from time timevalues[0], ignore previous values
	while ts[ts_index][0] < timevalues[0]:
		ts_index+= 1

	for index, time in enumerate(timevalues):
		n_values= 0
		sum_values= 0
		if(index== len(timevalues)-1):		# if this is the last bucket, take average of all remaining values in timeseries
			sum_values= sum(map(lambda x:x[1], ts[ts_index:-1]))
			n_values= len(ts) - ts_index
		else:					# otherwise take average of values till start of next bucket
			while ts[ts_index][0] < timevalues[index+1]:
				n_values+= 1
				sum_values+= ts[ts_index][1]
				ts_index+= 1
		if (n_values > 0):
			new_series.append(sum_values/n_values)
		elif(len(new_series)>0):
			new_series.append(new_series[-1])	# append the last value
		else:
			new_series.append( 0)			# if no prev. value available append 0
	
	return new_series
			

def find_common_timeinterval(slist):	# returns a time interval common to all ts in slist
	mintime= max([series[0][0] for series in slist])
	maxtime= min([series[-1][0] for series in slist])

	return (mintime, maxtime)


def bucketize(slist, n_buckets):		# trims one or a list of timeseries so that all contain common times and then bucketizes them
	if type(slist[0]) is list:
		(mintime, maxtime)= find_common_timeinterval(slist)
	else:
		mintime= slist[0][0]
		maxtime= slist[-1][0]

	x= int((maxtime-mintime)/n_buckets)
	timevalues= range(int(mintime), int(maxtime), int((maxtime-mintime)/n_buckets))
	if type(slist[0]) is list:
		bucketlist= [fit_ts(series, timevalues) for series in slist]
	else:
		bucketlist= fit_ts(slist, timevalues)

	return bucketlist
