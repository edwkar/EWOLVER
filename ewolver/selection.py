import itertools
from ewolver.utils.math_ import mean as _mean
from ewolver.utils.math_ import stddev as _stddev


class SelectionScheme(object):
    def __init__(self, *pipeline):
        pipeline = list(pipeline)
        assert pipeline != []
        self._pipeline = pipeline

    def select(self, population, child_gen, rng):
        return _run_pipeline(self._pipeline, population,
                             child_gen, rng)


class PipelineComponent(object):
    def __call__(self, population, child_gen, rng):
        raise NotImplementedError


class Stopper(PipelineComponent):
    def __call__(self, _, __, ___):
        return []


class Truncater(PipelineComponent):
    def __init__(self, limit):
        self._limit = limit

    def __call__(self, population, child_gen, rng):
        return population[:self._limit]


class Splitter(PipelineComponent):
    def __init__(self, partition_fn, left_pipeline, right_pipeline):
        self._partition_fn = partition_fn
        self._left_pipeline = left_pipeline
        self._right_pipeline = right_pipeline

    def __call__(self, population, child_gen, rng):
        left, right = self._partition_fn(population, child_gen, rng)

        left = _run_pipeline(self._left_pipeline, left, child_gen, rng)
        right = _run_pipeline(self._right_pipeline, right, child_gen, rng)

        return left + right


def ChildrenSieve():
    return Splitter(
        _adults_and_children,
        [Stopper],
        []
    )


def ElitismSieve(elite_size):
    return Splitter(
        _adults_and_children,
        [Ranker(), Truncater(elite_size)],
        [Ranker()]
    )


class UniqueFilter(PipelineComponent):
    def __call__(self, population, _, __):
        seen = set()
        res = []
        for p in population:
            if not str(p) in seen:
                res.append(p)
                seen.add(str(p))
        return res


class Ranker(PipelineComponent):
    def __call__(self, population, child_gen, rng):
        ranked_population = population[:]
        ranked_population.sort(lambda a, b: -cmp(a.fitness, b.fitness))
        return ranked_population


class RouletteWheel(PipelineComponent):
    def __init__(self, scaler, res_size):
        self._scaler = scaler
        self._res_size = res_size

    def __call__(self, population, child_gen, rng):
        fitness_vals = [p.fitness for p in population]

        scaled_fitness_vals = self._scaler(fitness_vals, child_gen)
        scaled_sum = float(sum(scaled_fitness_vals))

        wheel = []
        start_point = 0
        for i, p in enumerate(population):
            wheel.append((start_point, p,))
            start_point += scaled_fitness_vals[i]/scaled_sum
        wheel.append((1, None),) # Sentinel

        res = []
        for num in range(self._res_size):
            p = rng.random()
            for i in range(len(wheel)):
                if wheel[i][0] <= p < wheel[i+1][0]:
                    res.append(wheel[i][1])
                    break
        assert len(res) == self._res_size
        return res


def RankScaler(min_, max_):
    def scaler(fitness_vals, _):
        n = len(fitness_vals)
        fitness_vals_and_ids = zip(fitness_vals, range(n))
        fitness_vals_and_ids.sort()
        ranks = [id_ for _, id_ in fitness_vals_and_ids]
        def exp_(i):
            return min_ + (max_-min_)*ranks.index(i)/float(n-1)
        return map(exp_, range(n))
    return scaler


def _run_pipeline(pipeline, population, child_gen, rng):
    selected = population[:]
    for component in pipeline:
        selected = component(selected, child_gen, rng)
    return selected


def _adults_and_children(population, child_gen, rng):
    adults, children = [], []
    for p in population:
        assert p.birth_generation <= child_gen
        if p.birth_generation == child_gen:
            children.append(p)
        else:
            adults.append(p)
    return adults, children
