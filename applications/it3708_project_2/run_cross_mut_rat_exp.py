import time
from izhikevich import *


def _run_experiment_with_dict(dict_):
    return run_experiment(**dict_)


def run_rate_test_experiment():
    num_rounds_per_conf = 20
    pool = multiprocessing.Pool(processes=num_rounds_per_conf)

    all_res_str = ''

    for crossover_rate in [0.6, 0.7, 0.8]:
        for mutation_rate in [0.02, 0.03, 0.05, 0.1]:
            for ref_file_id in [1, 2, 3, 4]:
                ref_file = 'data/izzy-train%d.dat' % ref_file_id
                for diff_measure in ['spike-time', 'spike-interval', 'waveform']:
                    tpre = time.time()
                    proc_inputs = [dict(
                        _ref_file=ref_file,
                        _diff_measure=diff_measure,
                        rng=random.Random(seeder.randint(0, 0x81549300)),
                        num_generations=300,
                        _adult_pop_size=100,
                        _parent_pop_size=170,
                        _crossover_rate=crossover_rate,
                        _mutation_rate=mutation_rate,
                        _batch_mode=True
                    ) for _ in range(num_rounds_per_conf)]
                    res = pool.map(_run_experiment_with_dict, proc_inputs)
                    all_res_str += '  ' + repr(
                            [crossover_rate, mutation_rate,
                             ref_file, diff_measure, res]
                    ) + ',\n'
                    print time.time() - tpre

                    print len(all_res_str.split('\n'))
                    with open('res.txt', 'w') as f:
                        f.write(all_res_str)




if __name__ == '__main__':
    multiprocessing.freeze_support()

    run_rate_test_experiment()
    import sys
    sys.exit(0)
