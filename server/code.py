#!/usr/bin/python

import web

urls = (
  '/', 'Index',
  '/data', 'Data',
  '/anomalies', 'Anomalies',
  '/annotations', 'Annotations'
)

class Index:
  def GET(self):
    return "Hello, world!"

class Data:
  def GET(self):
    return "Hello, world!"

class Anomalies:
  def GET(self):
    return "Hello, world!"

class Annotations:
  def POST(self):
    return "Hello, world!"

if __name__ == "__main__": 
  app = web.application(urls, globals())
  app.run()