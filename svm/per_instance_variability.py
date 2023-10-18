import numpy as np

def getPercentile(latency_data, percentile):
    return np.percentile(latency_data, percentile)

def PCC(X, Y):
    n = len(X)
    sum_X = sum(X)
    sum_Y = sum(Y)
    sum_XY = sum(x * y for x, y in zip(X, Y))
    sum_X_squared = sum(x**2 for x in X)
    sum_Y_squared = sum(y**2 for y in Y)

    numerator = (n * sum_XY - sum_X * sum_Y)
    denominator = ((n * sum_X_squared - sum_X**2) * (n * sum_Y_squared - sum_Y**2)) ** 0.5

    if denominator == 0:
        return 0
    else:
        return numerator / denominator


def get_params(path):
    totalLatency = sum([span['duration'] for span in path])
    T99 = getPercentile([span['duration'] for span in path], 99)
    T50 = getPercentile([span['duration'] for span in path], 50)
    Ci = T99/T50
    values = []
    for i in path:
        Ti = i['duration']
        Ri = PCC([Ti], [totalLatency])
        values.append(Ri)
    return (values, Ci)