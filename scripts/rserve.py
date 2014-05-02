import pyRserve
import os, sys
import config

reqd_packages = ["TTR", "RHmm"]
reqd_sources = ["anomalies.r"]

class RGateway:
    def __init__(self):
        self.conn = pyRserve.connect()
        self.conn.voidEval('setwd("' + config.SCRIPTS_DIR + '")')
        for pkg in reqd_packages:
            conn.voidEval('library("' + pkg + '")')
        for src in reqd_sources:
            conn.voidEval('source("' + src + '")')

    def detect_SMA(self, path, window=100, threshold=100):
        streval= 'v <- detect_SMA("' + path + '", window=' + str(window) + '", threshold=' + str(threshold) + ')'
        print streval
        conn.voidEval(streval)
        print type(conn.r.v)
        return conn.r.v.tolist()