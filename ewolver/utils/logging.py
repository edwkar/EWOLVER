import os
from ewolver.core import Listener
from ewolver.utils.colors import *


# Well, this is rather hairy-looking shit...

class StdoutLogger(Listener):
    def __init__(self):
        self._last_child_gen = 0

    def after_evaluation(self, genotypes, phenotypes):
        os.system('clear')
        print 'The population has %s members.' % YELLOW(len(genotypes))

    def after_adult_sieving(self, adult_ptypes):
        gens = [p.birth_generation for p in adult_ptypes]
        print '   ...%s individuals reached adulthood.' % (
                GREEN(len(adult_ptypes)),)
        print '   ...of these, %s were from the last round of reproduction.' % (
                GREEN(len([p for p in adult_ptypes
                           if p.birth_generation == self._last_child_gen])),)
        print '   ...the youngest is gen %s, while the oldest is gen %s.' % (
                GREEN(max(gens)), GREEN(min(gens)),)
        print '   ...the average birth gen is %s.' % (GREEN(sum(gens)//len(gens)),)
        adult_ptypes = adult_ptypes[:]
        adult_ptypes.sort(lambda a, b: -cmp(a.fitness, b.fitness))
        print
        for i, k in enumerate(adult_ptypes):
            if len(adult_ptypes) < 30 or i <= 25 or i >= len(adult_ptypes)-5:
                print '      %-12s  %s  %-12s  %-12s' % (GREEN(i),
                        (str(k)[:100]), YELLOW(k.fitness),
                        GREEN(k.birth_generation),)
        print
        print

    def after_generation_step(self, new_child_gen):
        print '   ...the next children will be generation %s.' % (
                GREEN(new_child_gen),)
        self._last_child_gen = new_child_gen

    def after_parent_sieving(self, adult_ptypes):
        print '   ...%s adults were selected (w/rpl.) as parents.' % (
                GREEN(len(adult_ptypes)),)

    def after_reproduction(self, child_gtypes):
        print '   ...reproduction yielded %s individuals.' % (
                GREEN(len(child_gtypes)),)
