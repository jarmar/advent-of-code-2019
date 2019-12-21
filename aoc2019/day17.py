#!/usr/bin/env python

import code
from collections import defaultdict, namedtuple
from itertools import chain
import re
import sys

from aoc2019.intcode import Computer


Vec = namedtuple("Vec", ["x", "y"])


def adjacent(vec):
    return (
        Vec(vec.x - 1, vec.y),
        Vec(vec.x + 1, vec.y),
        Vec(vec.x, vec.y - 1),
        Vec(vec.x, vec.y + 1),
    )


def is_crossing(candidate, tiles):
    required_scaffolds = [
        pos for pos in chain([candidate], adjacent(candidate)) if pos in tiles
    ]
    return all(tiles[pos] == "#" for pos in required_scaffolds)


def get_tiles(opcodes):
    com = Computer(opcodes)
    map_str = "".join(chr(i) for i in com.run())
    return {
        Vec(x, y): tile
        for (y, line) in enumerate(map_str.splitlines())
        for (x, tile) in enumerate(line)
    }


def part1(opcodes):
    tiles = get_tiles(opcodes)
    return sum(pos.x * pos.y for pos in tiles if is_crossing(pos, tiles))


class Direction:
    UP = Vec(0, -1)
    DOWN = Vec(0, 1)
    LEFT = Vec(-1, 0)
    RIGHT = Vec(1, 0)


rotate_left = {
    Direction.UP: Direction.LEFT,
    Direction.LEFT: Direction.DOWN,
    Direction.DOWN: Direction.RIGHT,
    Direction.RIGHT: Direction.UP,
}

rotate_right = {
    Direction.UP: Direction.RIGHT,
    Direction.RIGHT: Direction.DOWN,
    Direction.DOWN: Direction.LEFT,
    Direction.LEFT: Direction.UP,
}


ROBOT_DIR = {
    "^": Direction.UP,
    "v": Direction.DOWN,
    "<": Direction.LEFT,
    ">": Direction.RIGHT,
}


def add_vec(v_a, v_b):
    return Vec(v_a.x + v_b.x, v_a.y + v_b.y)


def get_scaffold_path(tiles, pos, direction):
    tiles = defaultdict(int, tiles)
    path = ""
    while True:
        # try forward
        forward = add_vec(pos, direction)
        if tiles[forward] == "#":
            path += "F"  # "forward"
            pos = forward
            continue
        # try left
        ccw = rotate_left[direction]
        if tiles[add_vec(pos, ccw)] == "#":
            path += "L"
            direction = ccw  # don't move, only rotate
            continue
        # try right
        cw = rotate_right[direction]
        if tiles[add_vec(pos, cw)] == "#":
            path += "R"
            direction = cw  # don't move, only rotate
            continue
        # nothing worked: reached the end
        break
    return path


def condense(instructions):
    # condense a string of instructions to the format expected by the robot.
    # this mostly consists of compressing runs of "F"
    res = []
    run = 0
    for instr in instructions:
        if instr == "F":
            run += 1
        elif instr == "L":
            if run:
                res.append(str(run))
            run = 0
            res.append("L")
        elif instr == "R":
            if run:
                res.append(str(run))
            run = 0
            res.append("R")
    if run:
        res.append(str(run))
    return ",".join(res)


def solve1(strings):
    # is there a substring s such that each string in strings can be expressed
    # by repeating s?
    shortest = min(strings, key=len)
    # if so, it must be a prefix of the shortest string
    for length in range(len(shortest)):
        s1 = shortest[: length + 1]
        if len(condense(s1)) > 20:
            break
        # try matching each string against 1+ repeats of s1
        regex = re.compile(f"({s1})+$")
        if all(regex.match(string) for string in strings):
            return s1
    return None


def solve2(strings):
    # are there two substrings s1 and s2, such that each string in strings can
    # be described as a sequence of s1 and s2?
    shortest = min(strings, key=len)
    # try all prefixes of the shortest string
    for length in range(len(shortest)):
        s2 = shortest[: length + 1]
        if len(condense(s2)) > 20:
            break
        split_by_s2 = [s for string in strings for s in string.split(s2) if s]
        if s1 := solve1(split_by_s2):
            return s1, s2
    return None, None


def solve3(string):
    for length in range(1, len(string)):
        # one of the strings must be a prefix of the entire thing.
        s3 = string[:length]
        # we're assuming that everywhere s3 (or s2 or s1) can be used, it _is_
        # used. this doesn't necessarily have to be the case, but it works for
        # my input at least.
        split_by_s3 = [s for s in string.split(s3) if s]
        s1, s2 = solve2(split_by_s3)
        if s1 is not None and s2 is not None:
            ops = ",".join(
                string.replace(s1, "A").replace(s2, "B").replace(s3, "C")
            )
            if len(ops) > 20:
                continue
            return ops, condense(s1), condense(s2), condense(s3)


def last(iterator):
    """Return the last element from an iterator."""
    item = None
    for item in iterator:
        pass
    return item


def part2(opcodes):
    tiles = get_tiles(opcodes)
    robot_pos, robot_dir = next(
        (pos, ROBOT_DIR[ch]) for (pos, ch) in tiles.items() if ch in ROBOT_DIR
    )
    scaffold_path = get_scaffold_path(tiles, robot_pos, robot_dir)
    lines = solve3(scaffold_path)
    full_input = "".join(line + "\n" for line in chain(lines, "n"))
    # modifying the input argument here, but it's not like we'll need it again
    opcodes[0] = 2
    com = Computer(opcodes, inp=(ord(ch) for ch in full_input))
    # ignore all the output except the last value
    return last(com.run())


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
