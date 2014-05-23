import sys
if __name__=='__main__':
    sys.path.insert(0, "..")
import server.config as config
import json, os, shutil

# create a data_dir with all timeseries from a machine
def create_machine_datadir(datadir_path, machinedir_path, machine_name):
    pathobj= config.paths(datadir= datadir_path)
    new_pathobj= config.paths(datadir= machinedir_path)

    paths= [os.path.join(pathobj.TS_DIR, machine_name + "-" + name + ".data") for name in find_machine_timeseries(machine_name)]
    json_paths= [os.path.join(pathobj.TS_JSON_DIR, machine_name + "-" + name + ".data") for name in find_machine_timeseries(machine_name)]

    if not os.path.exists(new_pathobj.DATA_DIR):
        os.mkdir(new_pathobj.DATA_DIR)
    if not os.path.exists(new_pathobj.TS_DIR):
        os.mkdir(new_pathobj.TS_DIR)
    if not os.path.exists(new_pathobj.TS_JSON_DIR):
        os.mkdir(new_pathobj.TS_JSON_DIR)
    for json_path, path in zip(json_paths, paths):
        shutil.copy(path, new_pathobj.TS_DIR)
        #shutil.copy(json_path, new_pathobj.TS_JSON_DIR)

def find_machine_timeseries(machine_name):  # returns list of timeseries names for a given machine name
    pathobj= config.paths()
    imp_file= open(os.path.join(pathobj.DATA_BASE_DIR, "important.json"), 'r')
    names= json.load(imp_file)
    imp_file.close()
    return names[machine_name]
    

if __name__=='__main__':
    sys.path.insert(0, "..")
    create_machine_datadir(sys.argv[1], sys.argv[2], sys.argv[3])
