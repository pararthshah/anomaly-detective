# converts timeseries files to json

import os, sys
from read_folder import read_folder
import json

def convert(inpath, outpath):
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	flag= 0
	for (name, series) in read_folder(inpath):
		outfile= os.path.join(outpath, name)
		if os.path.isfile(outfile):
			continue
		jsondata= dict()
		jsondata['values']= map(lambda x:x[1], series)
		jsondata['time']= map(lambda x:x[0], series)
		fout= open(outfile, 'w')
		fout.write(json.dumps(jsondata))
		fout.close()


if __name__=='__main__':
	inpath= os.path.join(os.getcwd(), sys.argv[1])
	outpath= os.path.join(os.getcwd(), sys.argv[2])

	convert(inpath, outpath)

