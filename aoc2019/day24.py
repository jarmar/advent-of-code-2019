#!/usr/bin/env python

from collections import defaultdict
from itertools import chain
import sys


def count_neighbours(grid, x, y):
    s = 0
    if x > 0:
        if grid[y][x - 1] == "#":
            s += 1
    if y > 0:
        if grid[y - 1][x] == "#":
            s += 1
    if x < len(grid[0]) - 1:
        if grid[y][x + 1] == "#":
            s += 1
    if y < len(grid) - 1:
        if grid[y + 1][x] == "#":
            s += 1
    return s


def step_coord(grid, x, y):
    if grid[y][x] == "#":
        if count_neighbours(grid, x, y) == 1:
            return "#"
        else:
            return "."
    else:
        if count_neighbours(grid, x, y) in (1, 2):
            return "#"
        else:
            return "."


def step_grid(grid):
    return tuple(
        tuple(step_coord(grid, x, y) for x, _ in enumerate(line))
        for y, line in enumerate(grid)
    )


def biodiversity(grid):
    s = 0
    for ix, ch in enumerate(chain(*grid)):
        if ch == "#":
            s += 2 ** ix
    return s


def part1(map_str):
    grid = tuple(tuple(ch for ch in l.strip()) for l in map_str.splitlines())
    seen = set()
    while grid not in seen:
        seen.add(grid)
        grid = step_grid(grid)
    return biodiversity(grid)


def adjacent_p2(x, y, z):
    # we don't talk about the center square
    if (x, y) == (2, 2):
        return []

    adjacent = []

    # look left
    if x == 0:
        # looking out
        adjacent.append((1, 2, z - 1))
    elif (x, y) == (3, 2):
        # looking in
        adjacent.extend((4, yy, z + 1) for yy in range(5))
    else:
        adjacent.append((x - 1, y, z))

    # look right
    if x == 4:
        # looking out
        adjacent.append((3, 2, z - 1))
    elif (x, y) == (1, 2):
        # looking in
        adjacent.extend((0, yy, z + 1) for yy in range(5))
    else:
        adjacent.append((x + 1, y, z))

    # look up
    if y == 0:
        # looking out
        adjacent.append((2, 1, z - 1))
    elif (x, y) == (2, 3):
        # looking in
        adjacent.extend((xx, 4, z + 1) for xx in range(5))
    else:
        adjacent.append((x, y - 1, z))

    # look down
    if y == 4:
        # looking out
        adjacent.append((2, 3, z - 1))
    elif (x, y) == (2, 1):
        # looking in
        adjacent.extend((xx, 0, z + 1) for xx in range(5))
    else:
        adjacent.append((x, y + 1, z))

    return adjacent


def count_neighbours_p2(grids, x, y, z):
    adjacent = adjacent_p2(x, y, z)
    ch = grids[z][y][x]
    n_neighbours = 0
    for x, y, z in adjacent:
        # avoid creating new levels that are not adjacent to any bugs, because
        # if they aren't adjacent to any bugs, they're going to stay empty for
        # this iteration anyway.
        # they might still stay empty (if each square is adjacent to 3+ bugs),
        # but this way, we never create more than one unnecessary level (in
        # each direction).
        if z not in grids and ch != "#":
            continue
        if grids[z][y][x] == "#":
            n_neighbours += 1
    return n_neighbours


def step_coord_p2(grids, x, y, z):
    if grids[z][y][x] == "#":
        if count_neighbours_p2(grids, x, y, z) == 1:
            return "#"
        else:
            return "."
    else:
        if count_neighbours_p2(grids, x, y, z) in (1, 2):
            return "#"
        else:
            return "."


def step_grid_p2(grids, z):
    return tuple(
        tuple(step_coord_p2(grids, x, y, z) for x, _ in enumerate(line))
        for y, line in enumerate(grids[z])
    )


def empty_grid():
    return tuple(tuple("." for _ in range(5)) for _ in range(5))


def iterate(grids):
    new_grids = defaultdict(empty_grid)
    # step_grid_p2 will potentially create new levels (see comment in
    # count_neighbours_p2).
    grids_to_scan = set(grids)
    for z in grids_to_scan:
        new_grids[z] = step_grid_p2(grids, z)
    # step any new levels that were implicitly created. note that this cannot
    # create additional levels, so there's no need for yet another loop.
    for z in set(grids) - grids_to_scan:
        new_grids[z] = step_grid_p2(grids, z)
    return new_grids


def count_bugs(grids):
    return len(
        [
            ch
            for grid in grids.values()
            for line in grid
            for ch in line
            if ch == "#"
        ]
    )


def part2(map_str, steps=200):
    grid = tuple(tuple(ch for ch in l.strip()) for l in map_str.splitlines())
    grids = defaultdict(empty_grid, {0: grid})
    for s in range(steps):
        grids = iterate(grids)
    return count_bugs(grids)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        map_str = f.read()

    print(f"part 1: {part1(map_str)}")
    print(f"part 2: {part2(map_str)}")
