import pyRserve
import os, sys

def run_hmm(path, n_states):	# accepts path to timeseries data, returns clusters of points
	conn= pyRserve.connect()
	srcpath= os.getcwd()	# assumes that hmm.r is in the same directory as this python file
	conn.eval('setwd("' + srcpath + '")')
	conn.eval('source("hmm.r")')
	conn.eval('library("RHmm")')
	streval= 'v <- run_hmm("' + path + '", n_states= ' + str(n_states) + ')'
	print streval
	conn.eval(streval)
	print type(conn.r.v)
	return conn.r.v.tolist()

def get_anomalies(path, n_states, ratio):
	v= run_hmm(path, n_states)
	hist= get_histogram(v)		# return sorted histogram
	print hist
	n_flagged= 0
	flagged_values= list()
	for index, value in enumerate(hist):
		if n_flagged < len(v) * ratio:
			n_flagged+= value
			flagged_values.append(index)

	print flagged_values, n_flagged	, float(n_flagged)/len(v)
	# get intervals
	curr_flagged= 0
	for index, value in enumerate(v):
		if value in flagged_values and curr_flagged== 0:
			start_int= index
			curr_flagged= 1
		if value not in flagged_values and curr_flagged== 1:
			intervals.append(start_int, index)
			curr_flagged= 0
	print intervals
	return intervals
				
def get_histogram(v):
	maxval= max(v)
	histogram= [0]*maxval
	for value in v:
		histogram[value]+= 1
	return sorted(histogram)

if __name__=="__main__":
	pwd= os.getcwd()
	path= os.path.join(pwd, sys.argv[1])
	v= run_hmm(path, int(sys.argv[2]))
	#intervals= get_anomalies(path, 10, 0.9)
	print len(v)

