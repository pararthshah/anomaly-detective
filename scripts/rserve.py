import pyRserve
import os, sys
import config

reqd_packages = ["RHmm"]
reqd_sources = ["anomalies.r"]

class RGateway:
    def __init__(self):
        self.conn = pyRserve.connect()
        self.conn.voidEval('setwd("' + config.SCRIPTS_DIR + '")')
        for pkg in reqd_packages:
            self.conn.voidEval('library("' + pkg + '")')
        for src in reqd_sources:
            self.conn.voidEval('source("' + src + '")')

    def detect_SMA(self, path, window=100, threshold=100):
        streval= 'v <- detect_SMA("' + path + '", window=' + str(window) + '", threshold=' + str(threshold) + ')'
        print streval
        self.conn.voidEval(streval)
        print type(self.conn.r.v)
        return self.conn.r.v.tolist()