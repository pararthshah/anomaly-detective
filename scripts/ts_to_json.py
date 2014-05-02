# converts timeseries files to json

import os, sys
from read_folder import read_folder
from read_timeseries import read_timeseries
import json

def convert(inpath, names, outpath):
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	index= 0
	for (name, series) in read_folder(inpath, names):
		print index
		index+= 1
		outname = name[:-5] + ".json"
		print outname
		outfile= os.path.join(outpath, name)
		fout= open(outfile, 'w')
		fout.write(json.dumps(series))
		fout.close()


if __name__=='__main__':
	inpath= os.path.join(os.getcwd(), sys.argv[1])
	names= os.path.join(os.getcwd(), sys.argv[2])
	outpath= os.path.join(os.getcwd(), sys.argv[3])

	convert(inpath, names, outpath)

