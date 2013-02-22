#include <stdexcept>
#include <string>
#include "izhikevich.hh"

using namespace std;

/*
void describe(const float *potentials) {
    for (int i = 0; i < SPIKE_TRAIN_LEN; ++i)
        printf("%lf ", potentials[i]);
    putchar('\n');

    SpikeTimes st;
    spikes_from_potentials(potentials, &st, SPIKE_TRAIN_LEN);
    for (int i = 0; i < st.cnt; ++i)
        printf("%d ", st.data[i]);
    putchar('\n');
}
*/

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

int main(int argc, char *argv[]) {
    /*
    if (argc == 2 && argv[1] == "--describe") {
        Neuron n = read_next_neuron();
        float potentials[SPIKE_TRAIN_LEN];
        potentials_from_neuron(n, potentials, SPIKE_TRAIN_LEN);
        describe(potentials);
        return 0;
    }

    if (argc == 3 && streq(argv[1], "--describe-file")) {
        float potentials[SPIKE_TRAIN_LEN];
        char *refPath = argv[2];
        potentials_from_file(refPath, potentials, SPIKE_TRAIN_LEN);
        describe(potentials);
        return 0;
    }
    */

    if (argc != 4)
        print_usage_and_exit(argv[0]);

    char *refPath = argv[1];
    int numNeurons = atoi(argv[2]);

    DiffMetric *diffMetric = 0;
    DiffMetricWaveform dm_w;

    string diffMetricStr(argv[3]);
    if (diffMetricStr == "spike-time")
        ; //diffMetric = DiffMetricSpikeTimes();
    else if (diffMetricStr == "spike-interval")
        ; /*diffMetric = DiffMetricSpikeDistance();  TODO */
    else if (diffMetricStr == "waveform")
        diffMetric = &dm_w;
    else
        throw runtime_error("Unknown distance metric specified.");

    Neuron refNeuron(refPath);

}
 #if 0
    float ref_potentials[SPIKE_TRAIN_LEN];
    SpikeTimes ref_st;

    potentials_from_file(refPath, ref_potentials, SPIKE_TRAIN_LEN);
    spikes_from_potentials(ref_potentials, &ref_st, SPIKE_TRAIN_LEN);

    float test_potentials[SPIKE_TRAIN_LEN];
    SpikeTimes test_st;

    for (int i = 0; i < numNeurons; ++i) {
        Neuron n = read_next_neuron();
        potentials_from_neuron(n, test_potentials, SPIKE_TRAIN_LEN);
        spikes_from_potentials(test_potentials, &test_st,
                                SPIKE_TRAIN_LEN);
        printf("%lf\n", diffMetric(test_potentials, &test_st,
                                    ref_potentials, &ref_st,
                                    SPIKE_TRAIN_LEN));
    }

    int foo;
    if (scanf("%d", &foo) != EOF)
        die_hard("Expected EOF at stdin.");

    return 0;
}


/*
 * UTITILIES
 */

float min(float x, float y) { return x < y ? x : y; }
float max(float x, float y) { return x > y ? x : y; }
bool streq(const char *a, const char *b) { return strcmp(a, b) == 0; }

void die_hard(const char *msg)
{
    fprintf(stderr, "ERROR: %s\n", msg);
    exit(EXIT_FAILURE);
}


#endif
