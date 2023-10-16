import random
import os
import subprocess
import time

TOTAL_TIME = 8*6 # seconds
PAUSE_TIME_MIN = 1 # seconds
PAUSE_TIME_MAX = 3 # seconds

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

duration = 10 # sec

def inject():
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

if __name__ == "__main__":
    total_time = 0
    while total_time <= TOTAL_TIME:
        inject()
        pause_time = random.randint(PAUSE_TIME_MIN, PAUSE_TIME_MAX)
        print('Injection round completed. Sleeping for %d seconds'%pause_time)
        time.sleep(pause_time)
        total_time += pause_time
