#!/usr/bin/python

import config
import sys

sys.path.insert(0,"../scripts")

import web
import os, sys, time
import json
import read_timeseries

rel_datapath= "../../cs341/data/week1"

urls = (
    '/', 'Index',
    '/metrics', 'Metrics',
    '/data', 'Data',
    '/anomalies', 'Anomalies',
    '/annotations', 'Annotations'
)

render = web.template.render('templates')

class Index:
    def GET(self):
        return render.index('Bob')

class Metrics:
    def GET(self):
        params = web.input()
        return "Metrics!"

class Data:
    def GET(self):
        params = web.input()
        web.header('Content-Type', 'application/json')
        # TODO: This is needed for CORS (AJAX)- Currently, our HTTP and
        # API servers are on different domains. Consider removing/refactoring.
        #web.header('Access-Control-Allow-Origin', '*')
        filename= params.machine + "." + params.metric
        path= os.path.join(os.getcwd(), rel_datapath, "json", filename)
        with open(path) as str_file:
            json_str= str_file.read()
            return json_str


class Anomalies:
    def GET(self):
        params = web.input()
        return "Anomalies!"

class Annotations:
    def POST(self):
        json_data = web.data()
        # get 'name' from json_data
        name= json.loads(json_data)['name']
        path= os.path.join(rel_datapath, "annotations", name + time.time())
        with open(path, 'w') as annotation_file:
            annotation_file.write(json_data)
        return "Annotations!"

if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
