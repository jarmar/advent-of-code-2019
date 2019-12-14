#!/usr/bin/env python

from collections import defaultdict
from dataclasses import dataclass
import itertools
from math import ceil
import sys
from typing import Dict


@dataclass
class Reaction:
    out_count: int
    inputs: Dict[str, int]


def part1(reactions, fuel_needed=1):
    needed = defaultdict(int, {"FUEL": fuel_needed})
    excess = defaultdict(int)
    # easier to store this separately, so we don't get it from popitem()
    needed_ore = 0
    while needed:
        needed_item, n_needed = needed.popitem()
        if n_needed == 0:
            # may have been temporarily needed, but filled from excess
            continue
        reaction = reactions[needed_item]
        do_times = ceil(n_needed / reaction.out_count)
        n_made = do_times * reaction.out_count

        excess[needed_item] = n_made - n_needed
        for inp_name, inp_count in reaction.inputs.items():
            inp_total_needed = inp_count * do_times
            if inp_name == "ORE":
                needed_ore += inp_total_needed
            else:
                needed[inp_name] += inp_total_needed
        resolve_needs_from_excess(needed, excess)
    return needed_ore


def resolve_needs_from_excess(needed, excess):
    # or maybe "def socialism(...):"?...
    for needed_item, n_needed in needed.items():
        if excess[needed_item]:
            to_take = min(n_needed, excess[needed_item])
            excess[needed_item] -= to_take
            needed[needed_item] -= to_take


def part2(reactions):
    # you could probably solve this in some more clever way, but part1 is
    # sufficiently fast that we can just binary search for the answer.
    one_trillion = 10 ** 12
    lower_bound = 0
    upper_bound = None
    # find an upper bound by trying 2^{1,2,3,...}
    for n in itertools.count():
        guess = 2 ** n
        needed = part1(reactions, guess)
        if needed < one_trillion:
            # save some work in the next loop
            lower_bound = guess
        elif needed > one_trillion:
            upper_bound = guess
            break
        else:
            return two_n  # excessively unlikely
    # binary search
    while upper_bound > lower_bound + 1:
        guess = (upper_bound + lower_bound) // 2
        needed = part1(reactions, guess)
        if needed < one_trillion:
            lower_bound = guess
        elif needed > one_trillion:
            upper_bound = guess
        else:
            return needed
    return lower_bound


TEST_0 = """\
10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL"""


TEST_1 = """\
9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL"""


LARGE_1 = """\
157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT"""


LARGE_2 = """\
2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF"""


LARGE_3 = """\
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX"""


def test1_case(contents, expected):
    reactions = dict(parse_reaction(line) for line in contents.split("\n"))
    assert expected == part1(reactions)


def test1():
    test1_case(TEST_0, 31)
    test1_case(TEST_1, 165)
    test1_case(LARGE_1, 13312)
    test1_case(LARGE_2, 180697)
    test1_case(LARGE_3, 2210736)


def parse_reaction(line):
    inputs_r, out_r = line.split(" => ")
    inputs = dict()
    for inp in inputs_r.split(", "):
        count, name = inp.split()
        inputs[name] = int(count)
    out_count, out_name = out_r.split()
    return out_name, Reaction(int(out_count), inputs)


if __name__ == "__main__":
    test1()
    with open(sys.argv[1]) as f:
        reactions = dict(parse_reaction(line) for line in f.readlines())
    print(f"part 1: {part1(reactions)}")
    print(f"part 2: {part2(reactions)}")
