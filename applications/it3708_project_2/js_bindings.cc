#include <stdexcept>
#include <string>
#include <sstream>
#include <vector>
#include <emscripten/emscripten.h>
#include "izhikevich.hh"

using namespace std;

template <typename T>
static void write_js_array(const string& name, const vector<T>& xs) {
    stringstream ss;
    ss << name << " = [";
    for (int i = 0, n = xs.size(); i < n; ++i)
        ss << xs[i] << (i != n-1 ? "," : "");
    ss << xs.size();
    ss << "]";
    emscripten_run_script(ss.str().c_str());
}

extern "C"
void izhikevichTest(
    float A_a, float A_b, float A_c, float A_d, float A_k,
    float B_a, float B_b, float B_c, float B_d, float B_k
) {
    Neuron A(A_a, A_b, A_c, A_d, A_k);
    Neuron B(B_a, B_b, B_c, B_d, B_k);

    write_js_array("__NEURON_A_POTENTIALS", A.potentials());
    write_js_array("__NEURON_A_SPIKE_TIMES", A.spikeTimes());

    write_js_array("__NEURON_B_POTENTIALS", B.potentials());
    write_js_array("__NEURON_B_SPIKE_TIMES", B.spikeTimes());

    DiffMetricSpikeTimes dm_st;
    DiffMetricWaveform dm_wf;

    stringstream ss;
    ss << "__ANALYSIS = '"
       << "   A, spike cnt: " << A.spikeTimes().size() << "/N"
       << "   B, spike cnt: " << B.spikeTimes().size() << "/N/N"
       << "Spike-time dist: " << dm_st(A, B) << "/N"
       << "  Waveform dist: " << dm_wf(A, B) << "/N"
       << "';";
    emscripten_run_script(ss.str().c_str());
};
