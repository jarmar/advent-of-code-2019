#!/usr/bin/env python

import sys


def fuel_required(mass):
    return (mass // 3) - 2


def part1(masses):
    return sum(fuel_required(mass) for mass in masses)


def recursive_fuel_required(mass):
    fuel_sum = 0
    while True:
        mass = fuel_required(mass)
        if mass < 0:
            break
        fuel_sum += mass
    return fuel_sum


def part2(masses):
    return sum(recursive_fuel_required(mass) for mass in masses)


def test1():
    assert fuel_required(12) == 2
    assert fuel_required(14) == 2
    assert fuel_required(1969) == 654
    assert fuel_required(100756) == 33583


def test2():
    assert recursive_fuel_required(14) == 2
    assert recursive_fuel_required(1969) == 966
    assert recursive_fuel_required(100756) == 50346


if __name__ == "__main__":
    test1()
    test2()

    masses = []
    with open(sys.argv[1]) as f:
        for line in f:
            masses.append(int(line))

    print(f"part 1: {part1(masses)}")
    print(f"part 2: {part2(masses)}")
