# read_folder: iterator returning (name, timeseries) where timeseries is a list in the folder specified by path (full path)
# read_folder_lazy: iterator returning (name, read_ts_iter), where read_ts_iter is itself an iterator over an individual timeseries file
import os
import sys
from read_timeseries import read_timeseries, read_ts_iter

class read_folder:
	def __init__(self, path, names=""):
#		print "path in read_folder:", path
		self.fullpath= os.path.abspath(path)
		if not names:
			with open(names) as f:
				names_list = f.readlines()
				self.filelist = map(lambda x: os.path.join(self.fullpath, x.strip()),names_list)
		else:
			self.filelist= [f for f in os.listdir(self.fullpath) if os.path.isfile(os.path.join(self.fullpath, f))]
#		print "self filelist:", self.filelist
		self.n_files= len(self.filelist)
		self.currfile= 0
	
	def __iter__(self):
		return self
	
	def next(self):
		self.currfile+= 1
		if self.currfile > self.n_files:
			raise StopIteration
		else:
			return (self.filelist[self.currfile-1], read_timeseries(os.path.join(self.fullpath, self.filelist[self.currfile-1])))

class read_folder_lazy(read_folder):
	def next(self):
		self.currfile+= 1
		if self.currfile > self.n_files:
			raise StopIteration
		else:
			return (self.filelist[self.currfile-1], read_ts_iter(os.path.join(self.fullpath, self.filelist[self.currfile-1])))
		
		
if __name__ == '__main__':
	count = 0
	for ts in read_folder(sys.argv[1], sys.argv[2]):
		#print len(ts)
		count += 1
	print count

