#!/usr/bin/env python

from collections import defaultdict
import sys


class Node(object):
    def __init__(self):
        self.inc = []
        self.out = []

    @property
    def edges(self):
        return self.inc + self.out


def count_stuff(graph, node, depth):
    return depth + sum(
        count_stuff(graph, child, depth + 1) for child in graph[node].out
    )


def make_graph(edges):
    graph = defaultdict(Node)
    for from_n, to_n in edges:
        graph[from_n].out.append(to_n)
        graph[to_n].inc.append(from_n)
    return graph


def dijkstra(graph, start, goal):
    unvisited = set(graph)
    dist = defaultdict(lambda: 999999999999999)
    dist[start] = 0
    curr = start
    steps = 0
    while True:
        for node in graph[curr].edges:
            steps += 1
            if node not in unvisited:
                continue
            dist[node] = dist[curr] + 1
        unvisited.remove(curr)
        curr = min(unvisited, key=dist.__getitem__)
        if curr == goal:
            break
    return dist[goal]


def part1(lines):
    edges = [line.strip().split(")") for line in lines]
    graph = make_graph(edges)
    return count_stuff(graph, "COM", 0)


def part2(lines):
    edges = [line.strip().split(")") for line in lines]
    graph = make_graph(edges)
    return dijkstra(graph, "YOU", "SAN") - 2


TEST1_IN = """\
COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L"""


def test1():
    assert 42 == part1(TEST1_IN.split())


TEST2_IN = """\
COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN"""


def test2():
    assert 4 == part2(TEST2_IN.split())


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    print(f"part 1: {part1(lines)}")
    print(f"part 2: {part2(lines)}")
