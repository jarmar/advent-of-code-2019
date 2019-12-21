#!/usr/bin/env python

from collections import defaultdict, namedtuple
from dataclasses import dataclass
import heapq
from itertools import chain, combinations
import sys
from typing import FrozenSet, Tuple


Vec = namedtuple("Vec", ["x", "y"])


Portal = namedtuple("Portal", ["pos", "level_delta"])


def adjacent(vec):
    return (
        Vec(vec.x - 1, vec.y),
        Vec(vec.x + 1, vec.y),
        Vec(vec.x, vec.y - 1),
        Vec(vec.x, vec.y + 1),
    )


def dijkstra(edges_fun, tiles, portals, start, goal):
    dist = defaultdict(lambda: 999999999999999)
    dist[start] = 0
    queue = [(0, start)]
    while queue:
        dist_to_curr, curr = heapq.heappop(queue)
        if curr == goal:
            return dist_to_curr
        for neighb in edges_fun(curr, tiles, portals):
            dist_to_neighb = dist_to_curr + 1
            if dist_to_neighb < dist[neighb]:
                dist[neighb] = dist_to_neighb
                heapq.heappush(queue, (dist_to_neighb, neighb))
    havoc = ValueError("grrr")
    raise havoc


def get_tiles(map_str):
    return {
        Vec(x, y): tile
        for (y, line) in enumerate(map_str.splitlines())
        for (x, tile) in enumerate(line)
    }


def vertical_portals(map_str):
    # see "horizontal_portals()"
    map_str_transposed = "\n".join("".join(col) for col in zip(*map_str.splitlines()))
    for name, pos in horizontal_portals(map_str_transposed):
        yield name, Vec(pos.y, pos.x)


def horizontal_portals(map_str):
    # yield the positions of the "." positions acting like portals, along with
    # their associated labels.
    for y, line in enumerate(map_str.splitlines()):
        for x, cs in enumerate(zip(line, line[1:], line[2:])):
            if cs[0] == "." and (name := "".join(cs[1:3])).isalpha():
                yield name, Vec(x, y)
            elif cs[2] == "." and (name := "".join(cs[:2])).isalpha():
                yield name, Vec(x + 2, y)


def level_delta(outer_xs, outer_ys, pos):
    if pos.x in outer_xs or pos.y in outer_ys:
        return -1
    else:
        return 1


def get_portals(map_str):
    # also returns the positions of the start and goal, since they are found
    # in the same way the portals are found.
    portal_labels = defaultdict(list)
    for name, pos in horizontal_portals(map_str):
        portal_labels[name].append(pos)
    for name, pos in vertical_portals(map_str):
        portal_labels[name].append(pos)

    start = portal_labels.pop("AA")[0]
    goal = portal_labels.pop("ZZ")[0]
    assert all(len(portal) == 2 for portal in portal_labels.values())

    portals = dict()
    # use these to determine whether a portal is an "inner" or "outer" portal,
    # which determines if it increases or decreases the level we're currently
    # in (for part 2).
    outer_ys = [2, len(map_str.splitlines()) - 3]
    outer_xs = [2, len(map_str.splitlines()[0]) - 3]
    for portal in portal_labels.values():
        deltas = [level_delta(outer_xs, outer_ys, p) for p in portal]
        portals[portal[0]] = Portal(portal[1], deltas[0])
        portals[portal[1]] = Portal(portal[0], deltas[1])
    return start, goal, portals


def part1edges(pos, tiles, portals):
    # part 1 uses the raw positions as nodes.
    for adj in adjacent(pos):
        if tiles[pos] == ".":
            yield adj
    if pos in portals:
        yield portals[pos].pos


def part1(map_str):
    tiles = get_tiles(map_str)
    start, goal, portals = get_portals(map_str)
    return dijkstra(part1edges, tiles, portals, start, goal)


Part2Node = namedtuple("Part2Node", ["pos", "level"])


def part2edges(node, tiles, portals):
    # part 2 uses (surprise!) Part2Nodes as nodes.
    for adj in adjacent(node.pos):
        if tiles[adj] == ".":
            yield Part2Node(adj, node.level)
    if node.pos in portals:
        portal = portals[node.pos]
        level = node.level + portal.level_delta
        # ensure that we don't use outer portals on the initial level
        if level >= 0:
            yield Part2Node(portal.pos, level)


def part2(map_str):
    tiles = get_tiles(map_str)
    start, goal, portals = get_portals(map_str)
    # start and end on level 0.
    start = Part2Node(start, 0)
    goal = Part2Node(goal, 0)
    return dijkstra(part2edges, tiles, portals, start, goal)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        map_str = f.read()

    print(f"part 1: {part1(map_str)}")
    print(f"part 2: {part2(map_str)}")
