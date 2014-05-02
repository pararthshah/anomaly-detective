#!/usr/bin/python

import web
import os, sys, time
import json
import config

sys.path.insert(0, config.SCRIPTS_DIR)

import read_timeseries
from rserve import RGateway
from core.hmm_interface import get_anomalies

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
        path = os.path.join(config.TS_DIR, filename)
        with open(path) as str_file:
            json_str = str_file.read()
            return json_str

class Anomalies:
    def GET(self):
        params = web.input()
	if params.method=='SMA':
		try:
		    filename = params.machine + "-" + params.metric + ".data"
		    path = os.path.join(config.TS_DIR, filename)
		    anomalies = r_gateway.detect_SMA(path, int(params.window), float(params.threshold))
		    return anomalies
		except Exception, e:
		    return str(e)
	elif params.method=='HMM':
		filename = params.machine + "-" + params.metric + ".data"
		path = os.path.join(os.getcwd(), "../data/week1/timeseries", filename)
		anomalies= get_anomalies(path, int(params.n_states), float(params.percentage)/100)
		return json.dumps(anomalies)
			

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
    app = web.application(urls, globals())
    app.run()
