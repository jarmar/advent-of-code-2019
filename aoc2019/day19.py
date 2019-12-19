#!/usr/bin/env python

import code
from collections import defaultdict, namedtuple, deque
from itertools import chain, product
import itertools
import re
import sys

from aoc2019.intcode import Computer


def scan(opcodes, x, y):
    if x < 0 or y < 0:
        return 0
    com = Computer(opcodes, inp=iter((x, y)))
    return next(com.run())


def part1(opcodes):
    grid_items = [scan(opcodes, x, y) for x in range(50) for y in range(50)]
    return len([item for item in grid_items if item == 1])


def find_beam_edge(opcodes, x, y, *, left):
    # use x as a starting guess to find the leftmost or rightmost position of
    # the beam for line y.
    # note that x _must_ be either inside the beam or on the side of the beam
    # corresponding to the edge being sought (on the left of the beam if looking
    # for the left edge).
    toward_beam = 1 if left else -1
    res = scan(opcodes, x, y)
    if res:
        for x in itertools.count(start=x, step=-toward_beam):
            if not scan(opcodes, x - toward_beam, y):
                return x
    else:
        for x in itertools.count(start=x, step=toward_beam):
            if scan(opcodes, x, y):
                return x


BeamLine = namedtuple("BeamLine", ["y", "x_l", "x_r"])


def beam_edges(opcodes):
    x_left, x_right = 0, 0
    for y in itertools.count():
        x_left = find_beam_edge(opcodes, x_left, y, left=True)
        # For my input, adding 3 is necessary to ensure we don't start on the
        # wrong side of the beam.
        x_right = find_beam_edge(opcodes, x_right + 3, y, left=False)
        yield BeamLine(y, x_left, x_right)


def part2(opcodes, width=100):
    gen_beam_edges = beam_edges(opcodes)
    lines = deque()
    # pre-fill the queue.
    for _ in range(width):
        lines.append(next(gen_beam_edges))
    while True:
        assert len(lines) == width
        # taking two lines 99 steps apart, is it possible to fit the 100x100
        # square?
        start_line = lines.popleft()
        end_line = lines[-1]
        if start_line.x_r >= end_line.x_l + width - 1:
            return end_line.x_l * 10000 + start_line.y
        # otherwise, append another line and keep going
        lines.append(next(gen_beam_edges))


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
