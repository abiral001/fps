import random
import os
import subprocess
import time

# configure node IP addresses, username, network dev, and location of the performance anomaly injector here
nodes = [
        '192.168.49.2'
]
username = 'docker'
password = ''
location = '/home/abiralp/Desktop/firm/anomaly-injector'
threads = 2
out = subprocess.Popen(['nproc'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout, stderr = out.communicate()
# threads = int(stdout)
dev = 'eth0' # eth0

disk = 10   # file size: Gb
rate = 10  # bandwidth limit: kbit
limit = 20 #
latency = 50 # network delay: ms
burst = 1024 # bucket size

commands = [
        './cpu %d',
        # './cpu %d %s %d' -- cores, intensity
        # './cpu-all-cores-with-affinity',
        # './cpu-all-cores',
        './mem %d',
        # './pmbw -Q -s %d -S %d'
        './l3 %d',
        # 'sysbench --duration=%d --threads=%d --rate=%d',
        'sysbench fileio --file-total-size=%dG --file-test-mode=rndrw --time=%d --threads=%d run',
        'sudo tc qdisc %s dev %s root tbf rate %dkbit burst %d latency 0ms', # 'loss 1%'
        # 'tc qdisc add dev %s root tbf rate %dkbit latency %dms burst %d'
        'sudo tc qdisc %s dev %s root netem delay %dms %dms'
]

# init
duration = 10  # sec
intensity = random.randint(0, 100)

def inject():
    # get the targets (ranging from 1 to all nodes)
    num_targets = random.randint(1, len(nodes))
    print('# of targets: ' + str(num_targets))
    targets = set()
    i = 0
    while i < num_targets:
        target = random.randint(0, len(nodes) - 1)
        if target not in targets:
            targets.add(target)
            i += 1
    print(targets)

    for i in targets:
        num_types = random.randint(0, len(commands))
        print('# of anomaly types to inject: ' + str(num_types))
        types = set()
        j = 0
        while j < num_types:
            victim = random.randint(0, len(commands) - 1)
            if victim not in types:
                types.add(victim)
                j += 1
        print(types)
        
        for anomaly_type in types:
            intensity = random.randint(0, 100)
            pswd = ''
            if password != '':
                pswd = ':'+password
            minikube_alternative = 'minikube ssh'
            # command = 'ssh '+username+pswd+'@' + nodes[i] + ' "cd ' + location + '; '
            command = minikube_alternative + ' "cd ' + location + '; '

            if anomaly_type == 0:
                # cpu - ./cpu %d
                command += commands[anomaly_type] % duration + '"' # (duration, cores, intensity)
            elif anomaly_type == 1:
                # memory - ./mem %d
                command += commands[anomaly_type] % duration + '"' # (duration, intensity)
            elif anomaly_type == 2:
                # llc - ./l3 %d
                command += commands[anomaly_type] % duration + '"' # (duration, intensity)
            elif anomaly_type == 3:
                # io - sysbench fileio --file-total-size=%dG --file-test-mode=rndrw --time=%d --threads=%d run
                command += 'cd test-files; ' + commands[anomaly_type] % (disk, duration, threads) + '"' # (duration, threads, intensity)
            elif anomaly_type == 4:
                # network - tc
                command += commands[anomaly_type] % ('add', dev, rate, burst) + '; sleep ' + str(duration) + '; ' + commands[anomaly_type] % ('delete', dev, rate, burst) + '"'
                continue
            elif anomaly_type == 5:
                # network delay - tc
                command += commands[anomaly_type] % ('add', dev, latency, latency/10) + '; sleep ' + str(duration) + '; ' + commands[anomaly_type] % ('delete', dev, latency, latency/10) + '"'
                continue
            print(command)
            os.system(command)

if __name__=="__main__":
    while True:
        inject()
        print('Injection round completed...')
        time.sleep(2*60)
