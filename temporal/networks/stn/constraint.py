# Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py
#
# MIT License
#
# Copyright (c) 2019 HEATlab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from temporal.networks.distempirical import norm_sample, uniform_sample


class Constraint(object):
    """ Represents a temporal constraint between two nodes in the STN
        i: starting node
        j: ending node

        The constraint
        i --- [-wji, wij] ---> j
        Maps to two edges in a distance graph
        i --- wij ---> j
        i <--- -wji --- j

        -wji is the lower bound (minimum allocated time between i and j)
         wij is the upper bound (maximum allocated time between i and j)

        If there is no upper bound, its value is set to infinity and the edge from i to j does not exist
        Eg, i ---[4, inf] ---> j
        is mapped to
        i <--- -4 --- j
    """

    def __init__(self, i=0, j=0, wji=-1, wij='inf'):
        # node where the constraint starts
        self.starting_node_id = i
        # node where the constraint ends
        self.ending_node_id = j
        # Minimum allocated time between i and j
        self.min_time = -wji
        # Maximum allocated time between i and j
        if wij == 'inf':
            wij = float('inf')
        self.max_time = wij

    def __repr__(self):
        return "Constraint {} => {} [{}, {}]".format(self.starting_node_id, self.ending_node_id, -self.min_time, self.max_time)

    def to_dict(self):
        constraint_dict = dict()
        constraint_dict['starting_node_id'] = self.starting_node_id
        constraint_dict['ending_node_id'] = self.ending_node_id
        constraint_dict['min_time'] = - self.min_time
        if self.max_time == float('inf'):
            self.max_time = 'inf'
        constraint_dict['max_time'] = self.max_time
        return constraint_dict

    @staticmethod
    def from_dict(constraint_dict):
        constraint = Constraint()
        constraint.starting_node_id = constraint_dict['starting_node_id']
        constraint.ending_node_id = constraint_dict['ending_node_id']
        constraint.min_time = -constraint_dict['min_time']
        if constraint_dict['max_time'] == 'inf':
            constraint_dict['max_time'] = float('inf')
        constraint.max_time = constraint_dict['max_time']
        return constraint
