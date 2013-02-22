#include <algorithm>
#include <cstdio>
#include <cassert>
#include <cmath>
#include <stdexcept>
#include "izhikevich.hh"

using namespace std;

static bool __isConfigured = false;
static IzhikevichConfig __Config;
const IzhikevichConfig * const Config = &__Config;

void izhikevich_setup(IzhikevichConfig Config) {
    if (__isConfigured)
        throw logic_error("already configured");
    __Config = Config;
    __isConfigured = true;
}

static void ensure_initialized() {
    if (!__isConfigured)
        throw logic_error("time span has not been set");
}

Neuron Neuron::readNext() {
    ensure_initialized();

    float a, b, c, d, k;
    if (scanf("%f %f %f %f %f", &a, &b, &c, &d, &k) != 5)
        throw runtime_error("Neuron::readNext(), scanf failed");
    return Neuron(a, b, c, d, k);
}

v_pot_t Neuron::potsFromParams(float a, float b, float c, float d, float k) {
    ensure_initialized();

    v_pot_t res;
    res.reserve(Config->timespan);

    float v = Config->v_0;
    float u = Config->u_0;

    for (int i = 0; i < Config->timespan; ++i) {
        float dv = 1.0/Config->T * (k*v*v + 5*v + 140 - u + Config->I);
        float du = a/Config->T * (b*v - u);
        v += dv;
        u += du;
        res.push_back(min(Config->actThreshold, v));
        if (v >= Config->actThreshold) {
            v = c;
            u = u+d;
        }
    }

    return res;
}

v_pot_t Neuron::potsFromFile(const string& path) {
    ensure_initialized();

    v_pot_t res;
    res.reserve(Config->timespan);

    FILE *f;
    if ((f = fopen(path.c_str(), "r")) == NULL)
        throw runtime_error("fopen");
    for (int num_read = 0; num_read < Config->timespan; ++num_read) {
        float v;
        if (fscanf(f, "%f", &v) != 1)
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
    ensure_initialized();

    v_st_t res;
    for (int t = 0; t < Config->timespan; ++t)
        if (pot[t] >= Config->actThreshold)
            res.push_back(t);

    return res;
}

float DiffMetricSpikeTimes::operator()(const Neuron& a, const Neuron& b)
const {
    ensure_initialized();

    auto stA = a.spikeTimes(),
         stB = b.spikeTimes();

    int n = min(stA.size(), stB.size());

    float accum = 0;
    for (int i = 0; i < n; ++i)
        accum += abs(pow(stA[i]-stB[i], Config->p));

    return (pow(accum, 1.0/Config->p)) / n;
}

float DiffMetricWaveform::operator()(const Neuron& a, const Neuron& b)
const {
    ensure_initialized();

    float accum = 0;
    for (int i = 0; i < Config->timespan; ++i)
        accum += abs(pow(a[i]-b[i], Config->p));

    return (pow(accum, 1.0/Config->p)) / Config->timespan;
}
