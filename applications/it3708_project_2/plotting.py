import matplotlib
matplotlib.use('gtkagg')
import Queue
import pylab as pl
import threading
import time
from ewolver.core import Listener


_is_initialized = [False]
_new_data_lock = threading.Condition()
_new_data = [None]

def _start(ref_pot, ref_spike_times):
    if _is_initialized[0]:
        raise Exception("")
    _is_initialized[0] = True

    # Start interactive mode
    pl.ion()

    pl.grid(True)
    #pl.axis([0, 1001, -200, 300])
    pl.title('Best fitness')

    pl.plot(range(len(ref_pot)), ref_pot, color='black')

    def plot_spikes(x, color):
        print x
        pl.plot(range(len(ref_pot)),
                [35 if t in x else 0 for t in range(len(ref_pot))],
                color=color)

    def drawer():
        x, y = [], []
        while True:
            _new_data_lock.acquire()
            _new_data_lock.wait()
            assert _new_data[0] != None
            best_pot, best_st = _new_data[0]
            _new_data_lock.release()
            pl.gcf().clear()
            pl.plot(range(len(best_pot)), ref_pot, color='black')
            plot_spikes(ref_spike_times, 'blue')
            pl.plot(range(len(best_pot)), best_pot, color='red')
            pl.draw()

    t = threading.Thread(target=drawer)
    t.daemon=True
    t.start()


class _Listener(Listener):
    def __init__(self):
        self._bests = []

    def after_adult_sieving(self, adult_ptypes):
        best_p_type = max(adult_ptypes, key=lambda p: p.fitness)
        _new_data_lock.acquire()
        _new_data[0] = (best_p_type.potentials, best_p_type.spike_times,)
        _new_data_lock.notifyAll()
        _new_data_lock.release()


def setup_live_plotting_listener(ref_pot, ref_spike_times):
    _start(ref_pot, ref_spike_times)
    return _Listener()
