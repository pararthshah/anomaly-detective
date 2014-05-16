#!/usr/bin/python

import web
import os, sys, time
import json
import config

#DATAPATH= "../data/dataset1"    
sys.path.insert(0, config.BASE_DIR)
#paths= config.paths()
#sys.path.insert(0, paths.BASE_DIR)

from core import hmm_interface
from core.gateway import get_anomalies
from scripts.ma import detect_SMA

urls = (
    '/', 'Index',
    '/metrics', 'Metrics',
    '/data', 'Data',
    '/anomalies', 'Anomalies',
    '/annotations', 'Annotations'
)
render = web.template.render('templates')

#r_gateway = RGateway()

class Index:
    def GET(self):
        return render.index('Bob')

class Metrics:
    def GET(self):
        params = web.input(name="important")
        try:
            imp_file = open(os.path.join(config.DATA_DIR, params.name+".json"))    
            imp_json = imp_file.read()
            return imp_json
        except Exception, e:
            return str(e)

class Data:
    def GET(self):
        params = web.input()
        web.header('Content-Type', 'application/json')
        filename = params.machine + "-" + params.metric + ".data"
        path = os.path.join(config.TS_JSON_DIR, filename)
        with open(path) as str_file:
            json_str = str_file.read()
            return json_str

class Anomalies:
    def GET(self):
        params = web.input()
        filename = params.machine + "-" + params.metric + ".data"
        path = os.path.join(config.TS_DIR, filename)
        try:
            if params.method=='MA':
                anomalies= get_anomalies(path, "naive", "deviance")
                #anomalies = detect_SMA(path, int(params.window), float(params.threshold))
                return json.dumps(anomalies)
            elif params.method=='HMMX':
                anomalies= hmm_interface.get_anomalies(path, int(params.n_states), float(params.percentage)/100)
                return json.dumps(anomalies)
            elif params.method=='HMM':
                #anomalies= get_anomalies(path, "hmm", None, percent= float(params.percentage))
                anomalies= get_anomalies(path, "tmv", None, percent= float(params.percentage))
                return json.dumps(anomalies)
            elif params.method== 'NAIVE':
                anomalies= get_anomalies(path, "naive", "var", window_size= 30)
                return json.dumps(anomalies)
        except Exception, e:
            print "Exception:"
            print e
            return str(e)

class Annotations:
    def POST(self):
        json_data = web.data()
        # get 'name' from json_data
        name = json.loads(json_data)['name']
        path = os.path.join(config.ANNOTATIONS_DIR, name + "_" + time.time() + ".json")
        with open(path, 'w') as annotation_file:
            annotation_file.write(json_data)
        return "Annotations!"

if __name__ == "__main__": 
    #config.set_datadir(DATAPATH)    # remove to keep data path as ../data
    app = web.application(urls, globals())
    app.run()
