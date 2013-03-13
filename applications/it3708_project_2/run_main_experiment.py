from izhikevich import *


TO_SAVE = """
data/izzy-train1.dat_spike-time_2.png
data/izzy-train1.dat_spike-interval_3.png
data/izzy-train1.dat_waveform_3.png

data/izzy-train2.dat_spike-time_1.png
data/izzy-train2.dat_spike-interval_2.png
data/izzy-train2.dat_waveform_4.png

data/izzy-train3.dat_spike-time_2.png
data/izzy-train3.dat_spike-interval_4.png
data/izzy-train3.dat_waveform_3.png

data/izzy-train4.dat_spike-time_2.png
data/izzy-train4.dat_spike-interval_4.png
data/izzy-train4.dat_waveform_2.png
"""


for ref_file in ['data/izzy-train1.dat',
        'data/izzy-train2.dat', 'data/izzy-train3.dat',
        'data/izzy-train4.dat']:
    for diff_measure in ['spike-time', 'spike-interval', 'waveform']:
        for k in range(5):
            name = '%s_%s_%d.png' % (ref_file, diff_measure, k,)
            rng = random.Random(seeder.randint(0, 80000))
            if not name in TO_SAVE:
                continue
            run_experiment(
                ref_file,
                diff_measure,
                rng,
                num_generations=250,
                _adult_pop_size=100,
                _parent_pop_size=170,
                _crossover_rate=0.6,
                _mutation_rate=0.06,
                _batch_mode=False,
                _k=k
            )
