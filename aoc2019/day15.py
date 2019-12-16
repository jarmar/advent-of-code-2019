#!/usr/bin/env python

from collections import defaultdict, namedtuple
import sys

from aoc2019.intcode import Computer


Vec = namedtuple("Vec", ["x", "y"])


MOVE_INSTR = {
    Vec(0, -1): 1,
    Vec(0, 1): 2,
    Vec(-1, 0): 3,
    Vec(1, 0): 4,
}

UNKNOWN = -1
WALL = 0
SPACE = 1
OXYGEN = 2

GRAFIX = {UNKNOWN: " ", WALL: "#", SPACE: ".", OXYGEN: "O"}


def stringify(tiles):
    min_x = min(v.x for v in tiles)
    max_x = max(v.x for v in tiles)
    min_y = min(v.y for v in tiles)
    max_y = max(v.y for v in tiles)
    return "\n".join(
        "".join(GRAFIX[tiles[Vec(x, y)]] for x in range(min_x, max_x + 1))
        for y in range(min_y, max_y + 1)
    )


def adjacent(vec):
    return (
        Vec(vec.x - 1, vec.y),
        Vec(vec.x + 1, vec.y),
        Vec(vec.x, vec.y - 1),
        Vec(vec.x, vec.y + 1),
    )


def collect_path(curr, start, came_from):
    path = [curr]
    while curr != start:
        curr = came_from[curr]
        path.append(curr)
    return list(reversed(path))


def a_star(tiles, start, goal):
    """Find the shortest path from start to goal.

    For intermediate steps, _only_ uses positions which are known free spaces
    (i.e. tiles[pos] is either SPACE or OXYGEN).
    """
    dist = defaultdict(lambda: 999999999999999)
    dist[start] = 0
    came_from = dict()
    to_visit = {start}
    while True:
        # use taxicab_dist as heuristic
        curr = min(
            to_visit,
            key=lambda coords: dist[coords] + taxicab_dist(coords, goal),
        )
        if curr == goal:
            return collect_path(curr, start, came_from)
        to_visit.remove(curr)
        for neighbour in adjacent(curr):
            if tiles[neighbour] not in (SPACE, OXYGEN) and neighbour != goal:
                # only go into known open spaces or into the goal
                continue
            dist_via_curr = dist[curr] + 1
            if dist_via_curr < dist[neighbour]:
                # found a better route to this node
                dist[neighbour] = dist_via_curr
                came_from[neighbour] = curr
                to_visit.add(neighbour)


def path_to_moves(path):
    return [Vec(to.x - fr.x, to.y - fr.y) for (fr, to) in zip(path, path[1:])]


class Robot:
    def __init__(self):
        self.instruction = None

    def move_instructions_out(self):
        while True:
            yield self.instruction

    def set_move(self, move):
        self.instruction = MOVE_INSTR[move]


def explore(opcodes):
    tiles = defaultdict(lambda: -1)
    robot = Robot()
    com = Computer(opcodes, inp=robot.move_instructions_out())
    status = com.run()
    curr_pos = Vec(0, 0)
    tiles[curr_pos] = SPACE
    targets = set(adjacent(curr_pos))
    while targets:
        # select an unexplored tile next to an explored tile, prefer tiles
        # closer to our position
        target = min(targets, key=lambda v: taxicab_dist(v, curr_pos))
        targets.remove(target)
        path = a_star(tiles, curr_pos, target)

        moves = path_to_moves(path)
        # all moves except the last one are just through known territory, so
        # don't bother recording the result
        for move in moves[:-1]:
            robot.set_move(move)
            assert next(status) in (SPACE, OXYGEN)
        # got to the second-to-last position
        curr_pos = path[-2]

        # the result of the last move is where we actually learn something
        robot.set_move(moves[-1])
        tiles[target] = next(status)
        if tiles[target] in (SPACE, OXYGEN):
            # successfully moved to a new position, update curr_pos
            # (curr_pos was also set above to the path's penultimate position)
            curr_pos = target
            # add any new frontiers
            targets.update(
                pos for pos in adjacent(curr_pos) if tiles[pos] == UNKNOWN
            )
    return tiles


def part1(opcodes):
    tiles = explore(opcodes)
    oxygen_pos = next(
        coords for coords, tile in tiles.items() if tile == OXYGEN
    )
    path_to_oxygen = a_star(tiles, Vec(0, 0), oxygen_pos)
    return len(path_to_oxygen) - 1


def taxicab_dist(v_a, v_b):
    return abs(v_a.x - v_b.x) + abs(v_a.y - v_b.y)


def part2(opcodes):
    tiles = explore(opcodes)
    oxygen_pos = next(
        coords for coords, tile in tiles.items() if tile == OXYGEN
    )
    # flood fill
    steps = -1
    fill_from = {oxygen_pos}
    while fill_from:
        steps += 1
        fill_from = set(
            adj_pos
            for fill_pos in fill_from
            for adj_pos in adjacent(fill_pos)
            if tiles[adj_pos] == SPACE
        )
        for next_fill in fill_from:
            tiles[next_fill] = OXYGEN
    return steps


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
