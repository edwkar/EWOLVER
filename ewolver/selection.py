import itertools
from ewolver.utils.math_ import mean as _mean
from ewolver.utils.math_ import stddev as _stddev


def _separate_generations(population, child_gen):
    adults, children = [], []
    for p in population:
        assert p.birth_generation <= child_gen
        if p.birth_generation == child_gen:
            children.append(p)
        else:
            adults.append(p)
    assert children
    assert child_gen == 0 or adults
    return adults, children


class SelectionStrategy(object):
    def __init__(self, sel_protocol, sel_mechanism):
        self._sel_protocol = sel_protocol
        self._sel_mechanism = sel_mechanism

    # noinspection PyUnusedLocal
    def select(self, population, child_gen, number, rng):
        for_selection = self._sel_protocol.select(population, child_gen)
        selection_iterator = self._sel_mechanism.new_iterator(for_selection, rng)
        selected = list(itertools.islice(selection_iterator, number))
        assert len(selected) == number
        return selected


###########################
### SELECTION PROTOCOLS ###
###########################
class SelectionProtocol(object):
    def select(self, population, child_gen):
        raise NotImplementedError


class SelectAllSelectionProtocol(SelectionProtocol):
    def select(self, population, _):
        return population


class SelectChildrenSelectionProtocol(SelectionProtocol):
    def select(self, population, child_gen):
        _, children = _separate_generations(population, child_gen)
        assert children
        return children


############################
### SELECTION MECHANISMS ###
############################
class SelectionMechanism(object):
    def new_iterator(self, population, rng):
        """
        Should return an iterator yielding population members sorted in order
        of selection priority.
        """
        raise NotImplementedError


class RankSelectionMechanism(SelectionMechanism):
    def new_iterator(self, population, _):
        ranked_population = population[:]
        ranked_population.sort(lambda a, b: -cmp(a.fitness, b.fitness))
        assert ranked_population[0].fitness >= ranked_population[1].fitness
        yielded = set()
        for p in ranked_population:
            if not str(p) in yielded:
                yield p
                yielded.add(str(p))
        raise StopIteration


class RouletteWheelSelectionMechanism(SelectionMechanism):
    def __init__(self, fitness_scaler):
        self._fitness_scaler = fitness_scaler

    def new_iterator(self, population, rng):
        fitness_vals = [p.fitness for p in population]
        last_gen = max(p.birth_generation for p in population)
        scaled_fitness_vals = self._fitness_scaler(fitness_vals, last_gen)
        scaled_fitness_sum = float(sum(scaled_fitness_vals))

        wheel = []
        start_point = 0
        for i, p in enumerate(population):
            wheel.append( (start_point, p,) )
            start_point += scaled_fitness_vals[i]/scaled_fitness_sum
        wheel.append( (1, None), ) # Sentinel

        while True:
            p = rng.random()
            for i in range(len(wheel)):
                if wheel[i][0] <= p < wheel[i+1][0]:
                    yield wheel[i][1]
                    break


def fitness_proportionate_scaler(fitness_vals, _):
    return fitness_vals


def uniform_scaler(fitness_vals, __):
    return [0x42 for _ in fitness_vals]


def sigma_scaler(fitness_vals, _):
    mean, stddev = _mean(fitness_vals), _stddev(fitness_vals)
    if stddev == 0:
        return [1 for _ in fitness_vals]
    else:
        return [1 + (f-mean)/(2*stddev) for f in fitness_vals]


def new_boltzmann_scaler(t_for_gen):
    def boltzmann_scaler(fitness_vals, last_gen):
        T = t_for_gen(last_gen)
        fitness_vals_exp = [e**(f/T) for f in fitness_vals]
        exp_mean = _mean(fitness_vals_exp)
        return [f_exp/exp_mean for f_exp in fitness_vals_exp]
    return boltzmann_scaler


def new_rank_scaler(min_, max_):
    def rank_scaler(fitness_vals, _):
        n = len(fitness_vals)
        fitness_vals_and_ids = zip(fitness_vals, range(n))
        fitness_vals_and_ids.sort()
        ranks = [id_ for _, id_ in fitness_vals_and_ids]
        def exp_(i):
            return min_ + (max_-min_)*ranks.index(i)/float(n-1)
        return map(exp_, range(n))
    return rank_scaler


class TournamentSelectionMechanism(SelectionMechanism):
    def __init__(self, k, p_lucky):
        self._k = k
        self._p_lucky = p_lucky

    def new_iterator(self, population, rng):
        while True:
            group = rng.sample(population, self._k)
            if rng.random() <= self._p_lucky:
                yield rng.choice(group)
            else:
                best = group[0]
                for x in group:
                    if x.fitness > best.fitness:
                        best = x
                yield best


class SelectAllSelectionMechanism(SelectionMechanism):
    def new_iterator(self, population, rng):
        while True:
            for p in population:
                yield p
