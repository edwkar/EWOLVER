#include <algorithm>
#include <cstdio>
#include <cassert>
#include <cmath>
#include <stdexcept>
#include "izhikevich.hh"

using namespace std;

static IzhikevichConfig __config(1000,
                                 -60, 0,
                                 10.0, 10.0,
                                 35.0, 2.0);
const IzhikevichConfig * const Config = &__config;

void izhikevich_setup(IzhikevichConfig c) {
    __config = c;
}

Neuron Neuron::readNext() {
    double a, b, c, d, k;
    if (scanf("%lf %lf %lf %lf %lf", &a, &b, &c, &d, &k) != 5)
        throw runtime_error("Neuron::readNext(), scanf failed");
    return Neuron(a, b, c, d, k);
}

v_pot_t Neuron::potsFromParams(double a, double b, double c, double d, double k) {
    v_pot_t res;
    res.reserve(Config->timespan);

    double v = Config->v_0;
    double u = Config->u_0;

    for (int i = 0; i <= Config->timespan; ++i) {
        double dv = 1.0/Config->T * (k*v*v + 5*v + 140 - u + Config->I);
        double du = a/Config->T * (b*v - u);
        v += dv;
        u += du;
        res.push_back(min(Config->actThreshold, v));
        //res.push_back(v);
        if (v > Config->actThreshold) {
            v = c;
            u = u+d;
        }
    }

    return res;
}

v_pot_t Neuron::potsFromFile(const string& path) {
    v_pot_t res;
    res.reserve(Config->timespan);

    FILE *f;
    if ((f = fopen(path.c_str(), "r")) == NULL)
        throw runtime_error("fopen");
    for (int num_read = 0; num_read <= Config->timespan; ++num_read) {
        double v;
        if (fscanf(f, "%lf", &v) != 1)
            throw runtime_error("potentials_from_file, fscanf");
        res.push_back(v);
    }
    int foo;
    if (fscanf(f, "%d", &foo) != EOF)
        throw runtime_error("file length did not match expectation");
    fclose(f);

    return res;
}

v_st_t Neuron::spikeTimesFromPots(const v_pot_t &pot) {
    v_st_t res;

    for (int t = 0; t < Config->timespan; ++t)
        if (pot[t] >= Config->actThreshold)
            res.push_back(t);
    return res;
}

static double spikeCountPenalty(const Neuron& a, const Neuron& b) {
    int numA = a.spikeTimes().size(),
        numB = b.spikeTimes().size(),
        n = max(numA, numB),
        m = min(numA, numB),
        l = Config->timespan;
    return (n-m)*l / max(1.0, 2.0*m);
}

double DiffMetricSpikeTimes::operator()(const Neuron& a, const Neuron& b)
const {
    auto stA = a.spikeTimes(),
         stB = b.spikeTimes();

    int m = min(stA.size(), stB.size());

    double accum = 0;
    for (int i = 0; i < m; ++i)
        accum += pow(abs(stA[i]-stB[i]), Config->p);

    auto penalty = spikeCountPenalty(a, b);
    return (penalty + pow(accum, 1.0/Config->p))/max(1, m);
}

double DiffMetricSpikeIntervals::operator()(const Neuron& a, const Neuron& b)
const {
    auto stA = a.spikeTimes(),
         stB = b.spikeTimes();

    int m = min(stA.size(), stB.size());

    double accum = 0;
    for (int i = 1; i < m; ++i)
        accum += pow(abs((stA[i]-stA[i-1]) - (stB[i]-stB[i-1])), Config->p);

    auto penalty = spikeCountPenalty(a, b);
    return (penalty + pow(accum, 1.0/Config->p))/max(1, m);
}

double DiffMetricWaveform::operator()(const Neuron& a, const Neuron& b)
const {
    double accum = 0;
    for (int i = 0; i < Config->timespan; ++i)
        accum += abs(pow(a[i]-b[i], Config->p));

    return accum / Config->timespan;
    //return (pow(accum, 1.0/Config->p)) / Config->timespan;
}
