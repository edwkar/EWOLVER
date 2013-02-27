#include <stdexcept>
#include <string>
#include <cstdlib>
#include "izhikevich.hh"

using namespace std;

void describe(const Neuron& n) {
    auto pots = n.potentials();
    for (int i = 0; i < pots.size(); ++i)
        printf("%lf ", pots[i]);
    putchar('\n');

    auto st = n.spikeTimes();
    for (int i = 0; i < st.size(); ++i)
        printf("%d ", st[i]);
    putchar('\n');
}

void print_usage_and_exit(const char *prog_name) {
    printf("Usage: \n");
    printf("  %s [ref spike train path] [# neurons to test] [diff metric], or\n",
            prog_name);
    printf("  %s --describe\n\n",
            prog_name);
    printf("Diff metric:\n");
    printf("  spike-time | spike-interval | waveform\n");
    exit(1);
}

int main(int argc, char *_argv[]) {
    vector<string> argv;
    for (int i = 0; i < argc; ++i)
        argv.push_back(string(_argv[i]));

    if ((argc == 2 || argc == 3) && argv[1] == "--describe") {
        Neuron n = argc == 2 ? Neuron::readNext() : Neuron(argv[2]);
        describe(n);
        return EXIT_SUCCESS;
    }

    if (argc != 4) {
        print_usage_and_exit(_argv[0]);
        return EXIT_FAILURE;
    }

    string refPath = argv[1];
    Neuron refNeuron(refPath);

    int numNeurons = atoi(_argv[2]);

    DiffMetricSpikeTimes dm_st;
    DiffMetricSpikeIntervals dm_si;
    DiffMetricWaveform dm_w;

    string diffMetricStr = argv[3];
    DiffMetric *diffMetric;
    if (diffMetricStr == "spike-time")
        diffMetric = &dm_st;
    else if (diffMetricStr == "spike-interval")
        diffMetric = &dm_si;
    else if (diffMetricStr == "waveform")
        diffMetric = &dm_w;
    else
        throw runtime_error("unknown distance metric specified");

    for (int i = 0; i < numNeurons; ++i) {
        Neuron n = Neuron::readNext();
        printf("%lf\n", (*diffMetric)(n, refNeuron));
    }

    int foo;
    if (scanf("%d", &foo) != EOF)
        throw runtime_error("expected EOF at stdin");

    return EXIT_SUCCESS;
}
