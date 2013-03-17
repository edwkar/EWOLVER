import math
import random
from subprocess import (Popen, PIPE)
from ewolver import selection
from ewolver.core import *
from ewolver.binary import *
from ewolver.utils.logging import StdoutLogger
from ewolver.utils.math_ import mean as _mean, stddev as _stddev


BITS_PER_GENE = 12
SEEDER = random.Random(0x42)


def assert_2d_dims(tab, exp_num_rows, exp_num_cols):
    assert len(tab) == exp_num_rows
    for col in tab:
        assert len(col) == exp_num_cols


class ContinuousTimeRNN(object):
    def __init__(self, weights, bias, gain, time_constants):
        self._num_neurons = len(weights)
        self._weights = weights
        self._bias = bias
        self._gain = gain
        self._time_constants = time_constants
        self._y = [0 for _ in range(self._num_neurons)]
        self._o = [0 for _ in range(self._num_neurons)]
        self._has_updated = False

    def update(self, inputs):
        w = self._weights
        I = inputs
        bias = self._bias
        g = self._gain
        T = self._time_constants

        neuron_ids = range(self._num_neurons)

        def s_i(i):
            return sum(self._o[j] * w[i][j] + I[i]
                       for j in range(self._num_neurons))
        s = map(s_i, neuron_ids)

        def dy_i(i):
            return 1.0/T[i] * (-y[i] + s[i] + bias[i])
        dy = map(dy_i, neuron_ids)

        def o_i(i):
            return 1.0 / (1.0 + math.exp(-g[i] * y[i]))

        self._o = map(o_i, neuron_ids)
        self._y = [y_i + dy[i] for i in neuron_ids]

        self._has_updated = True

    def output(self, neuron_id):
        return self._o[neuron_id]

    has_updated = property(lambda self: self._has_updated)

    @staticmethod
    def factory_for_single_hidden_layer(num_inputs, num_hiddens, num_outputs):
        def id_map(from_, cnt):
            return [from_+i for i in range(cnt)]

        input_start = 0
        hidden_start = num_inputs
        output_start = num_inputs + num_hiddens
        num_neurons = num_inputs + num_hiddens + num_outputs
        zeroes = lambda: [0 for _ in range(num_neurons)]

        def create(input_to_hidden_weights,
                   hidden_bias, hidden_gain, hidden_tc,
                   hidden_to_hidden_weights,
                   hidden_to_output_weights,
                   output_bias, output_gain, output_tc,
                   output_to_output_weights):

            assert_2d_dims(input_to_hidden_weights, num_inputs, num_hiddens)
            assert (len(hidden_bias) == len(hidden_gain) == len(hidden_tc) ==
                    num_hiddens)
            assert_2d_dims(hidden_to_hidden_weights, num_hidden, num_hidden)
            assert_2d_dims(hidden_to_output_weights, num_hidden, num_outputs)
            assert (len(output_bias) == len(output_gain) == len(output_tc) ==
                    num_outputs)
            assert_2d_dims(output_to_output_weights, num_outputs, num_outputs)

            weights = map(zeroes, zeroes())
            bias = zeroes()
            gain = zeroes()
            tc   = zeroes()

            def set_props(bias_in, gain_in, tc_in, bias_out, shift):
                for i in range(len(bias_in)):
                    bias[shift+i] = bias_in[i]
                    gain[shift+i] = gain_in[i]
                    tc[shift+i]   = tc_in[i]

            def set_weights(tab, from_start, to_start):
                for i, row in enumerate(tab, start=from_start):
                    for j, v in enumerate(row, start=to_start):
                        weights[i][j] = v

            set_props(hidden_bias, hidden_gain, hidden_tc, hidden_start)
            set_props(output_bias, output_gain, output_tc, output_start)
            set_weights(input_to_hidden_weights, input_start, hidden_start)
            set_weights(hidden_to_hidden_weights, hidden_start, hidden_start)
            set_weights(hidden_to_output_weights, hidden_start, output_start)
            set_weights(output_to_output_weights, output_start, output_start)

            return ContinuousTimeRNN(weights, bias, gain, tc)

        return create


class TestCase(object):
    def __init__(self, world_width, world_height, paddle_width, paddle_pos):
        self._world_width = world_width
        self._world_height = world_height
        self._paddle_width = paddle_width
        self._paddle_pos = paddle_pos

    def test(self, neuron):


def setup_ea(num_inputs, num_hiddens, num_outputs):

