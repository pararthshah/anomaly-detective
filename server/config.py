#!/usr/bin/python

import os
import json


SERVER_DIR = os.path.abspath(os.path.dirname(__file__))

BASE_DIR = os.path.abspath(os.path.join(SERVER_DIR, os.pardir))

SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

CORE_DIR = os.path.join(BASE_DIR, "core")

DATA_DIR = os.path.join(BASE_DIR, "data")

DATA_BASE_DIR= DATA_DIR

TS_DIR = os.path.join(DATA_DIR, "timeseries")

TS_JSON_DIR = os.path.join(DATA_DIR, "timeseries_json")

ANOMALIES_DIR = os.path.join(DATA_DIR, "anomalies")

ANNOTATIONS_DIR = os.path.join(DATA_DIR, "annotations")

MACHINE_WTS_DIR = os.path.join(DATA_DIR, "machine_weights")

def set_datadir(datapath):   # data_dir_path is relative from server directory
    global DATA_DIR
    global TS_DIR
    global TS_JSON_DIR
    global ANOMALIES_DIR
    global ANNOTATIONS_DIR
    global MACHINE_WTS_DIR

    DATA_DIR = os.path.join(SERVER_DIR, datapath)

    TS_DIR = os.path.join(DATA_DIR, "timeseries")

    TS_JSON_DIR = os.path.join(DATA_DIR, "timeseries_json")

    ANOMALIES_DIR = os.path.join(DATA_DIR, "anomalies")

    ANNOTATIONS_DIR = os.path.join(DATA_DIR, "annotations")

    MACHINE_WTS_DIR = os.path.join(DATA_DIR, "machine_weights")

# f = open(os.path.join(DATA_DIR, "metrics.json"))

# METRICS_LIST = json.load(f)

# f.close()

