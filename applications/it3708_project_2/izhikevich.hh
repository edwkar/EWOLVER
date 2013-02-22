#ifndef _IZHIKEVICH_HH_
#define _IZHIKEVICH_HH_

#include <string>
#include <vector>

typedef std::vector<float> v_pot_t;
typedef std::vector<int> v_st_t;

class Neuron {
public:
    const bool hasUnknownParams;
    const float a, b, c, d, k;
private:
    const v_pot_t _potentials;
    const v_st_t _spikeTimes;

public:
    Neuron(float a, float b, float c, float d, float k) 
        : hasUnknownParams(false), a(a), b(b), c(c), d(d), k(k),
          _potentials(potsFromParams(a, b, c, d, k)),
          _spikeTimes(spikeTimesFromPots(_potentials)) {}

    Neuron(const std::string& potentialsFilePath)
        : hasUnknownParams(true), a(0), b(0), c(0), d(0), k(0),
          _potentials(potsFromFile(potentialsFilePath)),
          _spikeTimes(spikeTimesFromPots(_potentials)) {}

    const v_pot_t & potentials() const { return _potentials;  }
    const v_st_t & spikeTimes() const { return _spikeTimes; }

    int spikeCount() const { return _spikeTimes.size(); }
    int operator[](int idx) const { return _potentials.at(idx); }

    static Neuron readNext();

    static v_pot_t potsFromParams(float, float, float, float, float);
    static v_pot_t potsFromFile(const std::string&);
    static v_st_t spikeTimesFromPots(const v_pot_t&);
};


struct IzhikevichConfig {
    int timespan;
    float v_0, u_0,
          T, I, actThreshold, p;
    IzhikevichConfig(int timespan, float v_0, float u_0, float T, float I,
                     float actThreshold, float p) 
        : timespan(timespan), v_0(v_0), u_0(u_0), T(T), I(I),
          actThreshold(actThreshold), p(p) {}
    IzhikevichConfig() {}
};

class DiffMetric {
public:
    virtual float operator()(const Neuron&, const Neuron&) const = 0;
};

class DiffMetricSpikeTimes : public DiffMetric {
public:
    float operator()(const Neuron&, const Neuron&) const;
};

class DiffMetricSpikeDistance : public DiffMetric {
public:
    float operator()(const Neuron&, const Neuron&) const;
};

class DiffMetricWaveform : public DiffMetric {
public:
    float operator()(const Neuron&, const Neuron&) const;
};

void izhikevich_setup(IzhikevichConfig config);
extern const IzhikevichConfig * const Config;

#endif
