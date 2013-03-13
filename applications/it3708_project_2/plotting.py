import matplotlib
matplotlib.use('gtkagg')
import Queue
import pylab as pl
import threading
import time
from ewolver.core import Listener
from ewolver.utils.math_ import *


_ref = {}
_file_name = [None]



class _Listener(Listener):
    def __init__(self):
        self._bests = []
        self._reset()

    def _reset(self):
        self._mins = []
        self._means = []
        self._maxs = []
        self._stddevs = []
        self._best_pot = None

    def after_adult_sieving(self, adult_ptypes):
        fts = [p.fitness for p in adult_ptypes]
        self._mins.append(min(fts))
        self._means.append(mean(fts))
        self._maxs.append(max(fts))
        self._stddevs.append(stddev(fts))

        best_p_type = max(adult_ptypes, key=lambda p: p.fitness)
        self._best_pot = best_p_type.potentials

    def at_end(self):
        self._draw()
        self._reset()

    def _draw(self):
        N = range(len(_ref['pot']))

        pl.gcf().clear()
        pl.figure(figsize=(7, 4))
        pl.xlabel('Time', fontsize=12)
        pl.ylabel('Potential (mV)', fontsize=12)
        pl.grid(True)
        pl.title('Most fit individual at final iteration', fontsize=14)
        pl.plot(N, _ref['pot'], color='black', label='Reference spike train')
        pl.plot(N, self._best_pot, color='red', label='Evolved spike train')

        #pl.tight_layout()
        leg = pl.legend(loc=3, shadow=True, fancybox=True, prop={'size':12})
        leg.get_frame().set_alpha(0.6)
        pl.savefig(_file_name[0])


        N = len(self._maxs)
        X = range(N)

        pl.gcf().clear()
        pl.figure(figsize=(8, 5))
        ax1 = pl.subplot(111)
        pl.axis([0, N, self._means[1],
            max(self._stddevs)+.1*(max(self._stddevs)-self._means[1])])
        pl.xlabel('Generation', fontsize=12)
        pl.ylabel('Absolute fitness', fontsize=12)
        pl.grid(True)
        pl.title('Fitness development', fontsize=14)

        pl.plot(X, self._means, c='blue',  linewidth=2,
             label='Mean fitness')
        pl.plot(X, self._stddevs,  c='purple', linewidth=2,
             label='Standard deviation')
        leg = pl.legend(loc=3, shadow=True, fancybox=True, prop={'size':12})
        leg.get_frame().set_alpha(0.6)

        ax2 = pl.twinx()
        pl.axis([0, N, self._maxs[5],
            max(self._maxs)+.1*(max(self._maxs)-self._maxs[5])])
        pl.plot(X, self._maxs,  c='red',  linewidth=2,
             label='Maximum fitness')
        pl.ylabel('Absolute fitness', fontsize=12)

        leg = pl.legend(loc=4, shadow=True, fancybox=True, prop={'size':12})
        leg.get_frame().set_alpha(0.6)
        pl.savefig(_file_name[0].replace('.png', '.dev.png'))


def setup_live_plotting_listener(ref_pot, ref_spike_times, file_name):
    _ref['pot'] = ref_pot
    _ref['spike_times'] = ref_spike_times
    _file_name[0] = file_name
    return _Listener()
