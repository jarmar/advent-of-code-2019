#!/usr/bin/env python

from dataclasses import dataclass
from functools import reduce
import itertools
from math import gcd
import sys
from typing import List


@dataclass
class Moon:
    pos: List[int]
    vel: List[int]


def potential_energy(moon):
    return sum(abs(c) for c in moon.pos)


def kinetic_energy(moon):
    return sum(abs(c) for c in moon.vel)


def energy(moon):
    return potential_energy(moon) * kinetic_energy(moon)


def energy_after_steps(moons, steps):
    for _ in range(steps):
        for m1, m2 in itertools.combinations(moons, 2):
            for ix, (m1coord, m2coord) in enumerate(zip(m1.pos, m2.pos)):
                if m1coord < m2coord:
                    m1.vel[ix] += 1
                    m2.vel[ix] -= 1
                elif m1coord > m2coord:
                    m1.vel[ix] -= 1
                    m2.vel[ix] += 1
        for m in moons:
            for ix, vel in enumerate(m.vel):
                m.pos[ix] += vel
    return sum(energy(moon) for moon in moons)


def find_period(moons, coord_ix):
    # the simulation can also be run backwards, so for every state, there is
    # only one possible predecessor. hence, the first returning state must be
    # the initial one.
    coords = [m.pos[coord_ix] for m in moons]
    vels = [m.vel[coord_ix] for m in moons]
    start_coords = list(coords)
    start_vels = list(vels)

    moon_ixes = tuple(range(len(moons)))
    for step in itertools.count():
        for ix_a, ix_b in itertools.combinations(moon_ixes, 2):
            if coords[ix_a] < coords[ix_b]:
                vels[ix_a] += 1
                vels[ix_b] -= 1
            elif coords[ix_a] > coords[ix_b]:
                vels[ix_a] -= 1
                vels[ix_b] += 1
        for ix, vel in enumerate(vels):
            coords[ix] += vel
        if coords == start_coords and vels == start_vels:
            return step + 1


def lcm(a, b):
    return a * b // gcd(a, b)


TEST_LINES_1 = """\
<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>""".split(
    "\n"
)


TEST_LINES_2 = """\
<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>""".split(
    "\n"
)


def test1():
    assert 179 == energy_after_steps(parse_moons(TEST_LINES_1), 10)
    assert 1940 == energy_after_steps(parse_moons(TEST_LINES_2), 100)


def test2():
    assert 2772 == part2(parse_moons(TEST_LINES_1))
    assert 4686774924 == part2(parse_moons(TEST_LINES_2))


def part1(moons):
    return energy_after_steps(moons, 1000)


def part2(moons):
    # axes are independent, so calculate each axis's period independently
    periods = [find_period(moons, coord_ix) for coord_ix in range(3)]
    # find the lowest common multiple
    return reduce(lcm, periods)


def parse_moons(lines):
    moons = []
    for line in lines:
        # very nice
        pos = [int(p.split("=")[1]) for p in line.strip()[1:-1].split(",")]
        moons.append(Moon(pos=pos, vel=[0, 0, 0]))
    return moons


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    moons = parse_moons(lines)
    print(f"part 1: {part1(moons)}")
    print(f"part 2: {part2(moons)}")
