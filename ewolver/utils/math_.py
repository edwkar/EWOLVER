from math import sqrt


def mean(xs):
    return sum(xs)/float(len(xs))


def stddev(xs):
    xs_mean = mean(xs)
    return sqrt(1/float(len(xs)) * sum((x-xs_mean)**2 for x in xs))
