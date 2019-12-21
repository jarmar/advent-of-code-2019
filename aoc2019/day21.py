#!/usr/bin/env python

import code
from collections import defaultdict, namedtuple
from itertools import chain
import re
import sys

from aoc2019.intcode import Computer


THE_CODE = """\
NOT A J  # J = !A
NOT B T  # T = !B
OR J T   # T = !A | !B
NOT C J  # J = !C
OR J T   # T = (!A | !B | !C)
NOT D J  # J = !D
NOT J J  # J = D
AND T J  # J = D & (!A | !B | !C)
"""


THE_CODE_BOOGALOO = """\
NOT A J  # J = !A
NOT B T  # T = !B
OR J T   # T = !A | !B
NOT C J  # J = !C
OR J T   # T = (!A | !B | !C)
NOT I J  # J = !I
NOT J J  # J = I
OR  F J  # J = (F | I)
AND E J  # J = E & (F | I)
OR H J   # J = H | (E & (F | I))
AND D J  # J = D & (H | (E & (F | I)))
AND T J  # J = D & (H | (E & (F | I))) & (!A | !B | !C)
"""

# this was enough for me to get through the mission:
#
# AND (NOT A OR NOT B OR NOT C)  there's a gap
#     D                          we can land
#     OR                         (here's where it gets tricky)
#        H                       1.  we can jump immediately again
#        AND E                   2.  we can run one step, and then...
#            OR F                2a. ...run yet another step and hope for the best
#               I                2b. ...jump after running one step (to E)


def strip_comments(code):
    return "\n".join(line.split("#")[0].strip() for line in code.split("\n"))


def run_code(code, stride):
    inp = strip_comments(code) + stride + "\n"
    com = Computer(opcodes, inp=(ord(ch) for ch in inp))
    for i in com.run():
        if i > 256:
            return i
        print(chr(i), end="")


def part1(opcodes):
    return run_code(THE_CODE, "WALK")


def part2(opcodes):
    return run_code(THE_CODE_BOOGALOO, "RUN")


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
