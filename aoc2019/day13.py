#!/usr/bin/env python

from dataclasses import dataclass
from collections import defaultdict
from itertools import cycle, repeat
import sys
import os

from aoc2019.intcode import Computer
from aoc2019.utils import ichunks


GRAFIX = ["  ", "██", "🧱", "🧼", "⚽"]


def stringify(tiles):
    tiles = defaultdict(int, tiles)
    return "\n".join(
        "".join(GRAFIX[tiles[(x, y)]] for x in range(44)) for y in range(23)
    )


def part1(opcodes):
    tiles = dict()
    com = Computer(opcodes)
    for x, y, tile in ichunks(com.run(), 3):
        tiles[(x, y)] = tile
    return len([tile for tile in tiles.values() if tile == 2])


@dataclass
class Vec:
    x: int
    y: int

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y + other.y)


class Player:
    def __init__(self):
        self.last_ball = None
        self.joystick_action = 0

    def inform(self, tiles):
        ball_finder = (
            Vec(*coords) for coords, tile in tiles.items() if tile == 4
        )
        paddle_finder = (
            Vec(*coords) for coords, tile in tiles.items() if tile == 3
        )
        ball = next(ball_finder, None)
        paddle = next(paddle_finder, None)
        if ball is None or paddle is None:
            # redraw cycle or something like that
            return
        # do the thing
        self.joystick_action = self.give_thought_to(ball, paddle)
        self.last_ball = ball

    def hands(self):
        while True:
            yield self.joystick_action

    def give_thought_to(self, ball, paddle):
        # i am born, fully destitute of knowledge
        if self.last_ball is None:
            return 0

        # the ball is currently bouncing, don't mess with it
        if ball.x == paddle.x and ball.y == paddle.y - 1:
            return 0

        # just follow the ball, don't try to understand complex topics like
        # wall bounces. at least for my input, this was good enough
        vel = ball - self.last_ball
        next_ball = ball + vel
        if next_ball.x < paddle.x:
            return -1
        elif next_ball.x > paddle.x:
            return 1
        else:
            return 0


def part2(opcodes):
    opcodes = list(opcodes)
    opcodes[0] = 2
    tiles = dict()
    player = Player()
    com = Computer(opcodes, inp=player.hands())
    for x, y, outp in ichunks(com.run(), 3):
        if (x, y) == (-1, 0):
            score = outp
        else:
            tiles[(x, y)] = outp
            player.inform(tiles)
    return score


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
