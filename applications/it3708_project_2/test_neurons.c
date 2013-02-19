#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define SPIKE_TRAIN_LEN 1001

typedef struct {
    double a, b, c, d, k;
} Neuron;

typedef struct  {
    int cnt;
    int data[SPIKE_TRAIN_LEN];
} SpikeTimes;

typedef double (diff_metric_f)(const double[],
                               const SpikeTimes *,
                               const double[],
                               const SpikeTimes *,
                               int);

double min(double, double);
double max(double, double);
bool streq(const char *, const char *);
void die_hard(const char *);
void print_usage_and_exit(const char *);

Neuron read_next_neuron(void);
void read_activations_from_file(const char *, double *, int);
void spikes_from_activations(double *, SpikeTimes *, int);
void activations_from_neuron(Neuron, double *, int);

diff_metric_f spike_time_dist;
diff_metric_f spike_interval_dist;
diff_metric_f waveform_dist;

const double v_0 = -60;
const double u_0 = 0;

void describe_neuron(void) {
    Neuron n = read_next_neuron();

    double activations[SPIKE_TRAIN_LEN];
    activations_from_neuron(n, activations, SPIKE_TRAIN_LEN);
    for (int i = 0; i < SPIKE_TRAIN_LEN; ++i)
        printf("%lf ", activations[i]);
    putchar('\n');

    SpikeTimes st;
    spikes_from_activations(activations, &st, SPIKE_TRAIN_LEN);
    for (int i = 0; i < st.cnt; ++i)
        printf("%d ", st.data[i]);
    putchar('\n');
}

int main(int argc, char *argv[])
{
    if (argc == 2 && streq(argv[1], "--describe")) {
        describe_neuron();
        return 0;
    }

    if (argc != 4)
        print_usage_and_exit(argv[0]);

    char *ref_path = argv[1];
    int num_neurons = atoi(argv[2]);

    diff_metric_f *diff_metric = NULL;
    if (streq(argv[3], "spike-time"))
        diff_metric = spike_time_dist;
    else if (streq(argv[3], "spike-interval"))
        diff_metric = spike_interval_dist;
    else if (streq(argv[3], "waveform"))
        diff_metric = waveform_dist;
    else
        die_hard("Unknown distance metric specified.");

    double ref_activations[SPIKE_TRAIN_LEN];
    SpikeTimes ref_st;

    read_activations_from_file(ref_path, ref_activations, SPIKE_TRAIN_LEN);
    spikes_from_activations(ref_activations, &ref_st, SPIKE_TRAIN_LEN);

    double test_activations[SPIKE_TRAIN_LEN];
    SpikeTimes test_st;

    for (int i = 0; i < num_neurons; ++i) {
        Neuron n = read_next_neuron();
        activations_from_neuron(n, test_activations, SPIKE_TRAIN_LEN);
        spikes_from_activations(test_activations, &test_st,
                                SPIKE_TRAIN_LEN);
        printf("%lf\n", diff_metric(test_activations, &test_st,
                                    ref_activations, &ref_st,
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

double min(double x, double y) { return x < y ? x : y; }
double max(double x, double y) { return x > y ? x : y; }
bool streq(const char *a, const char *b) { return strcmp(a, b) == 0; }

void die_hard(const char *msg)
{
    fprintf(stderr, "ERROR: %s\n", msg);
    exit(EXIT_FAILURE);
}

void print_usage_and_exit(const char *prog_name)
{
    printf("Usage: \n");
    printf("  %s [ref spike train path] [# neurons to test] [diff metric], or\n",
            prog_name);
    printf("  %s --describe\n\n",
            prog_name);
    printf("Diff metric:\n");
    printf("  spike-time | spike-interval | waveform\n");
    exit(1);
}


/*
 * NEURON, SPIKE TRAIN, AND SPIKE COLLECTION CREATION
 */

Neuron read_next_neuron(void)
{
    double a, b, c, d, k;
    if (scanf("%lf %lf %lf %lf %lf", &a, &b, &c, &d, &k) != 5)
        die_hard("read_next_neuron: scanf failed");
    return (Neuron) { .a=a, .b=b, .c=c, .d=d, .k=k };
}

void read_activations_from_file(const char *path, double *st,
                                int num_exp)
{
    FILE *f;
    if ((f = fopen(path, "r")) == NULL)
        die_hard("fopen");

    for (int num_read = 0; num_read < num_exp; ++num_read)
        if (fscanf(f, "%lf", st+num_read) != 1)
            die_hard("read_activations_from_file, fscanf");

    int foo;
    if (fscanf(f, "%d", &foo) != EOF)
        die_hard("file length did not match expectation");

    fclose(f);
}

void spikes_from_activations(double *act, SpikeTimes *st,
                             int num_steps)
{
    const double threshold = 0;
    const int k = 5;

    st->cnt = 0;

    for (int i = 0; i < num_steps-k; ++i) {
        int t = i+k/2;
        if (act[t] <= threshold)
            continue;

        for (int j = i; j < i+k; ++j)
            if (j != t && act[j] >= act[t])
                continue;

        st->data[st->cnt++] = t;
    }
}

void activations_from_neuron(Neuron n, double *act,
                             int num_steps)
{
    const double T = 10.,
                 I = 10.,
                 threshold = 35;

    double v = v_0;
    double u = u_0;

    for (int i = 0; i < num_steps; ++i) {
        double dv = 1/T    * (n.k*v*v + 5*v + 140 - u + I);
        double du = n.a/T * (n.b*v - u);
        v += dv;
        u += du;
        act[i] = v;
        if (v > threshold) {
            v = n.c;
            u = u+n.d;
        }
    }
}


/*
 * DIFFERENCE METRICS.
 */

double spike_cnt_penalty(const SpikeTimes *st_a, const SpikeTimes *st_b,
                         int len) {
    int N = min(st_a->cnt, st_b->cnt),
        M = max(st_a->cnt, st_b->cnt),
        L = len;

    return (N-M)*L / (2*M);
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
const double p = 2;

double spike_time_dist(const double act_a[],
                       const SpikeTimes *st_a,
                       const double act_b[],
                       const SpikeTimes *st_b,
                       int len)
{
    int n = min(st_a->cnt, st_b->cnt);

    double accum = 0;
    for (int i = 0; i < n; ++i)
        accum += pow(abs(st_a->data[i] - st_b->data[i]), p);

    return (pow(accum, 1.0/p) + spike_cnt_penalty(st_a, st_b, len)) / n;
}

double spike_interval_dist(const double act_a[],
                           const SpikeTimes *st_a,
                           const double act_b[],
                           const SpikeTimes *st_b,
                           int len)
{
    int n = min(st_a->cnt, st_b->cnt);

    double accum = 0;
    for (int i = 1; i < n; ++i) {
        double d_a = st_a->data[i] - st_a->data[i-1],
               d_b = st_b->data[i] - st_b->data[i-1];
        accum += pow(abs(d_a - d_b), p);
    }

    return (pow(accum, 1.0/p) + spike_cnt_penalty(st_a, st_b, len)) / (n-1);
}

double waveform_dist(const double act_a[],
                     const SpikeTimes *st_a,
                     const double act_b[],
                     const SpikeTimes *st_b,
                     int len)
{
    double accum = 0;
    for (int i = 0; i < len; ++i)
        accum += abs(pow(act_a[i]-act_b[i], p));
    return pow(accum, 1.0/p) / len;
}
