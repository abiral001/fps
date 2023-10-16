import numpy as np

def getPercentile(latency_data, percentile):
    return np.percentile(latency_data, percentile)

def PCC(X, Y):
    return np.corrcoef(X, Y)[0, 1]

def get_params(path):
    totalLatency = sum([span['duration'] for span in path])
    T99 = getPercentile([span['duration'] for span in path], 99)
    T50 = getPercentile([span['duration'] for span in path], 50)
    Ci = T99/T50
    values = []
    for i in path:
        Ti = i['duration']
        Ri = PCC(Ti, totalLatency)
        values.append(Ri)
    return (values, Ci)