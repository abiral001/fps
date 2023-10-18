# simplifying this we can just scrape this api:
# http://192.168.49.2:32575/api/traces?lookback=2h&maxDuration=&minDuration=&service=nginx-web-server
import random
import os
import subprocess
import time
import requests
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn import svm
from joblib import load
from critical_path import get_cp
from per_instance_variability import get_params

SERVER_API = "http://192.168.49.2:31529"

TOTAL_TIME = 8*60 # seconds
PAUSE_TIME_MIN = 5 # seconds
PAUSE_TIME_MAX = 30 # seconds

#calculating total number of threads to use to saturate the machine
out = subprocess.Popen(['nproc'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout, stderr = out.communicate()
threads = int(stdout)
print("Total number of threads to use:", threads)

commands = [
    'sysbench cpu --threads=%d --cpu-max-prime=100000 run',
    'sysbench memory --memory-total-size=6G --memory-access-mode=rnd --threads=%d --memory-block-size=1M run',
    'sysbench fileio --file-num=512 --file-block-size=1638400 --file-total-size=2G --file-test-mode=seqwr --file-io-mode=sync --threads=%d run'
]

keys = [
    'cpu',
    'memory',
    'io'
]

collected = list()

model = SGDClassifier(loss = 'hinge', penalty='l2')
model = load('model/svm_model.joblib')

def inject(dataframe):
    num_types = random.randint(1, len(commands))
    print("No of anomaly types to inject: {}".format(num_types))
    types = set()
    j = 0
    while j < num_types:
        victim = random.randint(0, len(commands)-1)
        if victim not in types:
            types.add(victim)
            j+=1
    for anomaly_type in types:
        # intensity will change based on number of threads
        intensity = random.randint(1, threads) 
        command = commands[anomaly_type]%intensity
        print('Intensity of test %d'%intensity)
        final_command = 'minikube ssh "{}"'.format(command)
        print(final_command)
        os.system(final_command)
        # running the trace collector as soon as the injection is complete
        response = requests.get('{}/api/traces?limit=200&lookback=12h&service=nginx-web-server'.format(SERVER_API))
        trace_datas = json.loads(response.text)['data']
        for trace_data in trace_datas:
            if trace_data['traceID'] in collected:
                continue
            collected.append(trace_data['traceID'])
            longest_path = get_cp(trace_data)
            ri, ci = get_params(longest_path)
            for r in ri:
                result = model.predict(np.asarray([ci, r, intensity/16]).reshape((-1, 3)))[0]
                row = {
                    'ri': r,
                    'ci': ci,
                    'anomaly': True,
                    'localization': result,
                    'intensity': intensity,
                    'type': keys[anomaly_type],
                }
                dataframe = pd.concat([dataframe, pd.DataFrame([row])], ignore_index = True)
    return dataframe

if __name__ == "__main__":
    total_time = 0
    dataframe = pd.DataFrame()
    while total_time <= TOTAL_TIME:
        dataframe = inject(dataframe)
        pause_time = random.randint(PAUSE_TIME_MIN, PAUSE_TIME_MAX)
        print('Injection round completed. Sleeping for %d seconds'%pause_time)
        time.sleep(pause_time)
        total_time += pause_time
    dataframe.to_csv('result/injection_prediction.csv', index = False)


