#!/usr/bin/env python

from collections import namedtuple
from itertools import product
import sys


Crossing = namedtuple("Crossing", ["x", "y"])
HorizLine = namedtuple("HorizLine", ["x1", "x2", "y"])
VertLine = namedtuple("VertLine", ["x", "y1", "y2"])


def find_crossings(horiz_lines, vert_lines):
    crossings = []
    for horiz, vert in product(horiz_lines, vert_lines):
        x_lo, x_hi = min(horiz.x1, horiz.x2), max(horiz.x1, horiz.x2)
        y_lo, y_hi = min(vert.y1, vert.y2), max(vert.y1, vert.y2)
        if y_lo < horiz.y < y_hi and x_lo < vert.x < x_hi:
            crossings.append(Crossing(vert.x, horiz.y))
    return crossings


def find_closest_distance(horiz_lines, vert_lines):
    crossings = find_crossings(horiz_lines, vert_lines)
    return min(abs(cross.x) + abs(cross.y) for cross in crossings)


def make_lines(instrs):
    x, y = 0, 0
    horiz_lines = []
    vert_lines = []
    for direction, step in instrs:
        if direction == "U":
            vert_lines.append(VertLine(x, y, y + step))
            y = vert_lines[-1].y2
        elif direction == "D":
            vert_lines.append(VertLine(x, y, y - step))
            y = vert_lines[-1].y2
        elif direction == "R":
            horiz_lines.append(HorizLine(x, x + step, y))
            x = horiz_lines[-1].x2
        elif direction == "L":
            horiz_lines.append(HorizLine(x, x - step, y))
            x = horiz_lines[-1].x2
        else:
            raise ValueError("curses")
    return horiz_lines, vert_lines


def parse_lines(inp):
    instrs = parse_instrs(inp)
    return make_lines(instrs)


def part1(inputs):
    horiz_lines_a, vert_lines_a = parse_lines(inputs[0])
    horiz_lines_b, vert_lines_b = parse_lines(inputs[1])
    closest_q = find_closest_distance(horiz_lines_a, vert_lines_b)
    closest_r = find_closest_distance(horiz_lines_b, vert_lines_a)
    return min(closest_q, closest_r)


def get_distances(instrs):
    distances = dict()
    x, y, steps = 0, 0, 1
    for direction, step in instrs:
        # generate the list of new points, _in the order they appear_
        if direction == "U":
            next_y = y + step
            new_points = [(x, yy) for yy in range(y + 1, next_y + 1)]
            y = next_y
        elif direction == "D":
            next_y = y - step
            new_points = [(x, yy) for yy in reversed(range(next_y, y))]
            y = next_y
        elif direction == "R":
            next_x = x + step
            new_points = [(xx, y) for xx in range(x + 1, next_x + 1)]
            x = next_x
        elif direction == "L":
            next_x = x - step
            new_points = [(xx, y) for xx in reversed(range(next_x, x))]
            x = next_x
        else:
            raise ValueError("disdain")

        # only update distances for points not already seen
        for dist, coords in enumerate(new_points, start=steps):
            if coords not in distances:
                distances[coords] = dist
        steps += len(new_points)

    return distances


def part2(inputs):
    instrs_a = parse_instrs(inputs[0])
    distances_a = get_distances(instrs_a)

    instrs_b = parse_instrs(inputs[1])
    distances_b = get_distances(instrs_b)

    # assume that the wires never run along each other, or that it counts
    # as a crossing.
    shared = frozenset(distances_a).intersection(frozenset(distances_b))
    return min(distances_a[coords] + distances_b[coords] for coords in shared)


def parse_instrs(inp):
    return [(item[0], int(item[1:])) for item in inp.strip().split(",")]


def test1():
    assert 6 == part1(["R8,U5,L5,D3", "U7,R6,D4,L4"])
    assert 135 == part1(
        [
            "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
            "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7",
        ]
    )
    assert 159 == part1(
        [
            "R75,D30,R83,U83,L12,D49,R71,U7,L72",
            "U62,R66,U55,R34,D71,R55,D58,R83",
        ]
    )


def test2():
    assert 30 == part2(["R8,U5,L5,D3", "U7,R6,D4,L4"])
    assert 610 == part2(
        [
            "R75,D30,R83,U83,L12,D49,R71,U7,L72",
            "U62,R66,U55,R34,D71,R55,D58,R83",
        ]
    )
    assert 410 == part2(
        [
            "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
            "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7",
        ]
    )


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    print(f"part 1: {part1(lines)}")
    print(f"part 2: {part2(lines)}")
