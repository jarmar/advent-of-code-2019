#!/usr/bin/env python

from collections import defaultdict
from math import atan2
import sys

TEST_0 = """\
.#..#
.....
#####
....#
...##
""".split(
    "\n"
)

TEST_1 = """\
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
""".split(
    "\n"
)

TEST_2 = """\
#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.
""".split(
    "\n"
)

TEST_3 = """\
.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..
""".split(
    "\n"
)

TEST_4 = """\
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
""".split(
    "\n"
)

TEST_LASER = """\
.#....#####...#..
##...##.#####..##
##...#...#.#####.
..#.....#...###..
..#.#.....#....##
""".split(
    "\n"
)


def best_score_and_loc(lines):
    asteroids = asteroid_locations(lines)
    score_func = lambda loc: score(asteroids, loc)
    best_loc = max(asteroids, key=score_func)
    return (score_func(best_loc), best_loc)


def asteroid_locations(lines):
    return [
        (x, y)
        for (y, line) in enumerate(lines)
        for (x, ch) in enumerate(line)
        if ch == "#"
    ]


def dist_sq(loc1, loc2):
    xdiff = loc1[0] - loc2[0]
    ydiff = loc1[1] - loc2[1]
    return xdiff * xdiff + ydiff * ydiff


def score(asteroids, loc):
    # return the number of unique angles from loc to other asteroids
    return len(
        {
            atan2(asteroid[0] - loc[0], asteroid[1] - loc[1])
            for asteroid in asteroids
            if asteroid != loc
        }
    )


def order_by_arg_then_dist(asteroids, loc):
    arg_dist_asteroid = []
    for asteroid in asteroids:
        if asteroid == loc:
            continue
        # atan2 returns in (-pi, pi], so generate angles backwards and then
        # negate, in order to include the lower bound.
        arg = -atan2(asteroid[0] - loc[0], asteroid[1] - loc[1])
        # we clearly have no time for square roots
        dist = dist_sq(loc, asteroid)
        arg_dist_asteroid.append((arg, dist, asteroid))

    astr_by_arg = defaultdict(list)
    # sort by arg, then by distance (squared)
    # collect all asteroids with the same arg together, closest first
    for arg, dist, asteroid in sorted(arg_dist_asteroid):
        astr_by_arg[arg].append((dist, asteroid))
    return astr_by_arg


def destruction_order(asteroids, laser):
    astr_by_arg = order_by_arg_then_dist(asteroids, laser)
    while astr_by_arg:
        to_delete = []
        # rotate one turn...
        for arg, same_arg_astrs in astr_by_arg.items():
            # yield the closest item for this angle
            yield same_arg_astrs.pop(0)[1]
            # if no asteroids left for this angle, mark for deletion
            if not same_arg_astrs:
                to_delete.append(arg)
        # cannot delete during iteration, so do it afterwards
        for arg in to_delete:
            del astr_by_arg[arg]


def test1():
    assert best_score_and_loc(TEST_0) == (8, (3, 4))
    assert best_score_and_loc(TEST_1) == (33, (5, 8))
    assert best_score_and_loc(TEST_2) == (35, (1, 2))
    assert best_score_and_loc(TEST_3) == (41, (6, 3))
    assert best_score_and_loc(TEST_4) == (210, (11, 13))


def test2():
    asteroids = asteroid_locations(TEST_LASER)
    destr_order = list(destruction_order(asteroids, (8, 3)))
    assert destr_order[0] == (8, 1)
    assert destr_order[1] == (9, 0)
    assert destr_order[2] == (9, 1)
    assert destr_order[3] == (10, 0)
    assert destr_order[4] == (9, 2)
    assert destr_order[5] == (11, 1)
    assert destr_order[6] == (12, 1)
    assert destr_order[7] == (11, 2)
    assert destr_order[8] == (15, 1)

    assert destr_order[9] == (12, 2)
    assert destr_order[10] == (13, 2)
    assert destr_order[11] == (14, 2)
    assert destr_order[12] == (15, 2)
    assert destr_order[13] == (12, 3)
    assert destr_order[14] == (16, 4)
    assert destr_order[15] == (15, 4)
    assert destr_order[16] == (10, 4)
    assert destr_order[17] == (4, 4)

    assert destr_order[18] == (2, 4)
    assert destr_order[19] == (2, 3)
    assert destr_order[20] == (0, 2)
    assert destr_order[21] == (1, 2)
    assert destr_order[22] == (0, 1)
    assert destr_order[23] == (1, 1)
    assert destr_order[24] == (5, 2)
    assert destr_order[25] == (1, 0)
    assert destr_order[26] == (5, 1)

    asteroids = asteroid_locations(TEST_4)
    destr_order = list(destruction_order(asteroids, (11, 13)))
    assert destr_order[0] == (11, 12)
    assert destr_order[1] == (12, 1)
    assert destr_order[2] == (12, 2)
    assert destr_order[9] == (12, 8)
    assert destr_order[19] == (16, 0)
    assert destr_order[49] == (16, 9)
    assert destr_order[99] == (10, 16)
    assert destr_order[198] == (9, 6)
    assert destr_order[199] == (8, 2)
    assert destr_order[200] == (10, 9)
    assert destr_order[298] == (11, 1)


def part1(lines):
    return best_score_and_loc(lines)[0]


def part2(lines):
    _, laser = best_score_and_loc(lines)
    asteroids = asteroid_locations(lines)
    destr_order = list(destruction_order(asteroids, laser))
    the_one = destr_order[199]
    return the_one[0] * 100 + the_one[1]


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        lines = f.readlines()

    print(f"part 1: {part1(lines)}")
    print(f"part 2: {part2(lines)}")
