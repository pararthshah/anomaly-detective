#!/usr/bin/python

import web

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
        return "Data!"

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