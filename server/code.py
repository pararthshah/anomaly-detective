#!/usr/bin/python

import web
import json

urls = (
    '/', 'Index',
    '/metrics', 'Metrics',
    '/data', 'Data',
    '/anomalies', 'Anomalies',
    '/annotations', 'Annotations'
)

class Index:
    def GET(self):
        return "Hello, world!"

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
				web.header('Access-Control-Allow-Origin', '*')
				return json.dumps([[5, 2], [6, 3], [8, 2], [10,5], [16,8],[29,10]]);

class Anomalies:
    def GET(self):
        params = web.input()
        return "Anomalies!"

class Annotations:
    def POST(self):
        params = web.input()
        return "Annotations!"

if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
