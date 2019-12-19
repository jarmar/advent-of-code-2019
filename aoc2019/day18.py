#!/usr/bin/env python

from collections import defaultdict, namedtuple
from dataclasses import dataclass
import heapq
from itertools import chain, combinations
import sys
from typing import FrozenSet, Tuple


Vec = namedtuple("Vec", ["x", "y"])


def adjacent(vec):
    return (
        Vec(vec.x - 1, vec.y),
        Vec(vec.x + 1, vec.y),
        Vec(vec.x, vec.y - 1),
        Vec(vec.x, vec.y + 1),
    )


def print_map(tiles):
    """Print map, for debugging purposes."""
    min_x = min(pos.x for pos in tiles)
    max_x = max(pos.x for pos in tiles)
    min_y = min(pos.y for pos in tiles)
    max_y = max(pos.y for pos in tiles)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            print(tiles[Vec(x, y)], end="")
        print("")
    print("")


def a_star(tiles, start, goal):
    """Find the shortest path from start to goal."""
    dist = defaultdict(lambda: 999999999999999)
    dist[start] = 0
    came_from = dict()
    to_visit = {start}
    while to_visit:
        # use taxicab_dist as heuristic
        curr = min(
            to_visit,
            key=lambda coords: dist[coords] + taxicab_dist(coords, goal),
        )
        if curr == goal:
            return a_star_collect_path(curr, start, came_from)
        to_visit.remove(curr)
        for neighbour in adjacent(curr):
            if tiles[neighbour] == "#":
                continue
            dist_via_curr = dist[curr] + 1
            if dist_via_curr < dist[neighbour]:
                # found a better route to this node
                dist[neighbour] = dist_via_curr
                came_from[neighbour] = curr
                to_visit.add(neighbour)
    return None


def a_star_collect_path(curr, start, came_from):
    path = [curr]
    while curr != start:
        curr = came_from[curr]
        path.append(curr)
    return list(reversed(path))


def taxicab_dist(v_a, v_b):
    return abs(v_a.x - v_b.x) + abs(v_a.y - v_b.y)


def make_graph(tiles, start_nodes):
    """Make a neighbour dict graph."""
    graph = defaultdict(dict)
    tiles = defaultdict(str, tiles)
    all_keys = [
        (pos, tile)
        for (pos, tile) in tiles.items()
        if tile.islower() or tile in start_nodes
    ]
    for (fr_pos, fr_tile), (to_pos, to_tile) in combinations(all_keys, 2):
        # using A* is probably a bad choice here, using dijkstra once for each
        # node to find the distance to all other nodes should be better.
        path = a_star(tiles, fr_pos, to_pos)
        if path is None:
            continue
        # convert doors to lower so we can compare them to keys more easily.
        path_doors = frozenset(
            tiles[path_pos].lower()
            for path_pos in path
            if tiles[path_pos].isupper()
        )
        result = (len(path) - 1, path_doors)
        # don't create edges leading to the starting position(s)
        if to_tile.islower():
            graph[fr_tile][to_tile] = result
        if fr_tile.islower():
            graph[to_tile][fr_tile] = result
    return graph


def fancy_dijkstra(graph, start_node):
    n_keys = len([name for name in graph if name.islower()])
    dist = defaultdict(lambda: 999999999999999)
    dist[start_node] = 0
    queue = [(0, start_node)]
    while queue:
        dist_to_curr, curr = heapq.heappop(queue)
        if len(curr.keys) == n_keys:
            return dist_to_curr
        for neighb_node, edge_cost in curr.edges(graph):
            dist_to_neighb = dist_to_curr + edge_cost
            # this lookup is quite stupid - it checks whether we have a better
            # cost for this exact set of collected keys. of course, if we have
            # a better cost with a superset of the keys here, there's no reason
            # to save this cost.
            # checking for this "domination" criterion should be better
            # asymptotically, but in practice, at least the naive implementation
            # is considerably slower. it does use ~40% less memory, though.
            if dist_to_neighb < dist[neighb_node]:
                dist[neighb_node] = dist_to_neighb
                heapq.heappush(queue, (dist_to_neighb, neighb_node))
    havoc = ValueError("grrr")
    raise havoc


@dataclass(frozen=True)
class Part1Node:
    name: str
    keys: FrozenSet[str]

    def edges(self, graph):
        for to, (dist, doors) in graph[self.name].items():
            if doors.issubset(self.keys):
                to_keys = frozenset(chain(self.keys, (to,)))
                yield Part1Node(to, to_keys), dist

    def cmp_repr(self):
        return (len(self.keys), self.name)

    def __lt__(self, other):
        return self.cmp_repr().__lt__(other.cmp_repr())


def get_tiles(map_str):
    return {
        Vec(x, y): tile
        for (y, line) in enumerate(map_str.splitlines())
        for (x, tile) in enumerate(line)
    }


def part1(map_str):
    tiles = get_tiles(map_str)
    pairwise = make_graph(tiles, "@")
    start_node = Part1Node("@", frozenset())
    return fancy_dijkstra(pairwise, start_node)


@dataclass(frozen=True)
class Part2Node:
    name: Tuple[str]
    keys: FrozenSet[str]

    def edges(self, graph):
        for ix, fr in enumerate(self.name):
            for to, (dist, doors) in graph[fr].items():
                if doors.issubset(self.keys):
                    to_names = list(self.name)
                    to_names[ix] = to
                    to_keys = frozenset(chain(self.keys, (to,)))
                    yield Part2Node(tuple(to_names), to_keys), dist

    def cmp_repr(self):
        return (len(self.keys), self.name)

    def __lt__(self, other):
        return self.cmp_repr().__lt__(other.cmp_repr())


PART2_CENTER = """\
@#$
###
£#€"""


def part2_modify_map(tiles):
    start = next(pos for (pos, tile) in tiles.items() if tile == "@")
    center_tiles = get_tiles(PART2_CENTER)
    for delta, tile in center_tiles.items():
        tiles[Vec(start.x + delta.x - 1, start.y + delta.y - 1)] = tile


def part2(map_str):
    tiles = get_tiles(map_str)
    part2_modify_map(tiles)
    graph = make_graph(tiles, "@£$€")
    start_node = Part2Node(("@", "£", "$", "€"), frozenset())
    return fancy_dijkstra(graph, start_node)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        map_str = f.read()

    print(f"part 1: {part1(map_str)}")
    print(f"part 2: {part2(map_str)}")
