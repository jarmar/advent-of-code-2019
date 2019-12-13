#!/usr/bin/env python

from collections import defaultdict
import sys

from aoc2019.intcode import Computer

DIRECTIONS = ["N", "E", "S", "W"]


class Robot(object):
    def __init__(self):
        self.pos = [0, 0]
        self.direction = "N"

    def turn(self, toward):
        dir_ix = DIRECTIONS.index(self.direction)
        if toward == "CW":
            dir_ix += 1
        elif toward == "CCW":
            dir_ix -= 1
        else:
            raise ValueError(f"bogus toward {toward}")
        dir_ix %= len(DIRECTIONS)
        self.direction = DIRECTIONS[dir_ix]

    def move_forward(self):
        if self.direction == "N":
            self.pos[1] -= 1
        elif self.direction == "E":
            self.pos[0] += 1
        elif self.direction == "S":
            self.pos[1] += 1
        elif self.direction == "W":
            self.pos[0] -= 1
        else:
            raise ValueError(f"bogus dir {self.direction}")

    def camera(self, world):
        while True:
            try:
                yield world[tuple(self.pos)]
            except KeyError:
                yield 0


def paint_world(opcodes, start_color=None):
    robot = Robot()
    world = dict()
    if start_color is not None:
        world[tuple(robot.pos)] = start_color
    com = Computer(opcodes, inp=robot.camera(world))
    for ix, out in enumerate(com.run()):
        if ix % 2 == 0:
            world[tuple(robot.pos)] = out
        else:
            robot.turn(["CCW", "CW"][out])
            robot.move_forward()
    return world


def part1(opcodes):
    return len(paint_world(opcodes))


def part2(opcodes):
    painted = paint_world(opcodes, start_color=1)

    min_x = min(pos[0] for pos in painted)
    max_x = max(pos[0] for pos in painted)
    min_y = min(pos[1] for pos in painted)
    max_y = max(pos[1] for pos in painted)

    # while running the robot, we don't want defaultdict, since we need
    # len(...) for part1, but here it simplifies things.
    world_color = defaultdict(int, painted)
    return "\n".join(
        "".join("👮🚨"[world_color[(x, y)]] for x in range(min_x, max_x + 1))
        for y in range(min_y, max_y + 1)
    )


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2:\n{part2(opcodes)}")
