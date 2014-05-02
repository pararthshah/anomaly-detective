# dumps the list of important metrics to json

# if metrics.txt contains the regexs for important metrics, do the following:
# $ cd <data-dir>
# $ touch important.txt
# $ while read p; do ls timeseries | grep "$p" >> important.txt; done < metrics.txt

# Then run this script with
# $ python create_ts_list.py important.txt important.json

# To copy the actual data of the important time series:
# $ while read p; do cp -v <data-dir>/timeseries/$p outdir; done < important.txt

import os, sys
import json
import re

important_file = sys.argv[1]
output_file = sys.argv[2]

important = []

with open(important_file) as f:
    important = f.readlines()

output = {}
for line in important:
    if not line.strip().endswith(".data"):
        continue
    line = line.strip()[:-5]
    m = re.search("com-com", line)
    if m:
        index = m.start()+3
        machine = line[:index]
        metric = line[index+1:]
        if machine not in output:
            output[machine] = []
        output[machine].append(metric)

output_json = json.dumps(output, sort_keys=True, indent=4)

with open(output_file, 'w') as f:
    f.write(output_json)



