#!/usr/bin/env python
#
# This is a simple testcase purely for testing the autotuner on permutations
#
# http://en.wikipedia.org/wiki/Travelling_salesman_problem
#

import argparse
from builtins import range
from math import factorial

import opentuner
from opentuner.measurement import MeasurementInterface
from opentuner.search.manipulator import (ConfigurationManipulator,
                                          IntegerParameter)

parser = argparse.ArgumentParser(parents=opentuner.argparsers())
parser.add_argument('data', help='distance matrix file')


def encode_permutation(permutation):
    n = len(permutation)
    elements = sorted(permutation)  # Sorted list of elements for lexicographical order
    index = 0

    for i in range(n):
        current_element = permutation[i]
        rank = elements.index(current_element)

        # Contribution to the index
        index += rank * factorial(n - 1 - i)

        # Remove the current element from the list to avoid duplication
        elements.remove(current_element)

    return index

def decode_permutation(index, elements):
    n = len(elements)
    if index < 0 or index >= factorial(n):
        raise ValueError("Index out of bounds for the given set of elements.")

    elements = sorted(elements)  # Sort elements for consistent ordering
    permutation = []

    # Calculate which elements to choose
    for i in range(n):
        fact = factorial(n - 1 - i)
        pos = index // fact  # Determine the position of the next element
        permutation.append(elements[pos])  # Append the selected element
        index %= fact  # Update index for remaining elements

        # Remove the used element from the list to avoid duplication
        elements.pop(pos)

    return permutation

class TSP(MeasurementInterface):
    def __init__(self, args):
        super(TSP, self).__init__(args)
        data = args.data
        m = open(data).readlines()
        self.distance = [[int(i) for i in l.split()] for l in m]
        self.elements = list(range(len(self.distance)))

    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        p = decode_permutation(cfg[0], self.elements)
        t = self.eval_path(p)
        return opentuner.resultsdb.models.Result(time=t)

    def eval_path(self, p):
        """ Given permutation of cities as a list of indices,
        return total path length """
        out = sum(self.distance[p[i]][p[i + 1]] for i in range(len(p) - 1))
        ##        print out, p
        return out

    def manipulator(self):
        manipulator = ConfigurationManipulator()
        # manipulator.add_parameter(PermutationParameter(0, list(range(len(self.distance)))))
        manipulator.add_parameter(IntegerParameter(0, 0, factorial(len(self.elements)) - 1))
        return manipulator

    def solution(self):
        p = [1, 13, 2, 15, 9, 5, 7, 3, 12, 14, 10, 8, 6, 4, 11]
        return self.eval_path(p)


if __name__ == '__main__':
    args = parser.parse_args()
    TSP.main(args)
