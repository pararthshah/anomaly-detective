#!/usr/bin/python

import os
import json

SERVER_DIR = os.path.abspath(os.path.dirname(__file__))

BASE_DIR = os.path.abspath(os.path.join(SERVER_DIR, os.pardir))

SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

DATA_DIR = os.path.join(BASE_DIR, "data")

TS_DIR = os.path.join(DATA_DIR, "timeseries_json")

ANOMALIES_DIR = os.path.join(DATA_DIR, "anomalies")

ANNOTATIONS_DIR = os.path.join(DATA_DIR, "annotations")

# f = open(os.path.join(DATA_DIR, "metrics.json"))

# METRICS_LIST = json.load(f)

# f.close()

del os