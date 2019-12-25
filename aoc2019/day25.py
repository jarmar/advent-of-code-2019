#!/usr/bin/env python

from collections import defaultdict
import heapq
import re
import sys

from aoc2019.intcode import Computer


REVERSE = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}


class Crawler:
    def __init__(self, opcodes):
        self.com = Computer(opcodes, inp=self.get_input())
        self.run = self.com.run()
        self.buffer = ""
        self.quiet = False

    def play(self):
        # until we reach the goal, this function just keeps the computer
        # running, the actual logic happens in get_input().
        for i in self.com.run():
            if not self.quiet:
                print(chr(i), end="")
            self.buffer += chr(i)
        # output is done, no more input requested == success
        print(self.buffer)
        match = re.search(r"typing (\d+) on the keypad", self.buffer)
        return match[1]

    def get_input(self):
        # this function (and the functions it calls) use "yield from" to
        # run asynchronously when input is requested by the intcode computer.
        print("BOT: exploring...")
        items, cmd_to_test = yield from Explorer(self).explore_ship()
        print("BOT: ready to test using items:")
        print(*(f"    {item}" for item in items), sep="\n")
        print("BOT: trying different combinations", end="", flush=True)
        # avoid the deluge of similar printouts
        self.quiet = True
        yield from BruteForcer(self, cmd_to_test).outsmart_test(items)

    def get_buffered_output(self):
        result = self.buffer
        self.buffer = ""
        return result

    def emit(self, cmd):
        if not self.quiet:
            print(cmd)
        for ch in cmd + "\n":
            yield ord(ch)


class BruteForcer:
    def __init__(self, crawler, cmd_to_test):
        self.crawler = crawler
        self.cmd_to_test = cmd_to_test

    def outsmart_test(self, items):
        yield from self.try_with(items[0], items[1:])

    def attempt_to_enter(self):
        print(".", end="", flush=True)
        yield from self.crawler.emit(self.cmd_to_test)
        # after yielding, execution of this function stops until the intcode
        # computer requests more input => can read the output directly after
        # yielding.
        return self.crawler.get_buffered_output()

    def try_with(self, item, items):
        # precondition: "item" and "items" are all held by the bot.
        # try with and without holding "item", and recursively for all
        # items in "items".
        result = yield from self.attempt_to_enter()
        if "heavier" in result:
            # recursing isn't going to make us heavier
            return
        else:
            # prefer doing the "drop" branch first? it should fail faster,
            # so without any knowledge of which is the correct branch, it
            # seems reasonable to try it first.
            yield from self.crawler.emit(f"drop {item}")
            if items:
                yield from self.try_with(items[0], items[1:])
            else:
                yield from self.attempt_to_enter()

            # ...otherwise, pick it up again and recurse anew
            yield from self.crawler.emit(f"take {item}")
            if items:
                yield from self.try_with(items[0], items[1:])


class Explorer:
    def __init__(self, crawler):
        self.crawler = crawler
        # items picked up
        self.items = []
        # cardinal direction => room name
        self.graph = dict()
        self.pos = None
        self.last_pos = None
        self.last_command = None
        # used to generate placeholder names
        self.placeholder_ix = 0
        # command used to enter the test room
        self.cmd_to_test = None

    def generate_placeholder(self):
        self.placeholder_ix += 1
        return f"UNKNOWN_{self.placeholder_ix}"

    def examine_room(self, room_str):
        name, doors, items = parse_room(room_str)
        self.pos = name

        self.graph[self.pos] = dict()
        for door in doors:
            if REVERSE[door] == self.last_command:
                # replace the placeholder
                self.graph[self.last_pos][self.last_command] = name
                self.graph[self.pos][door] = self.last_pos
            elif name == "Security Checkpoint":
                # don't store this door in the graph
                self.cmd_to_test = door
            else:
                # create a placeholder node for unknown rooms
                # luckily, there are no loops in the maze
                self.graph[self.pos][door] = self.generate_placeholder()

        for item in items:
            if item in BAD_THINGS_DO_NOT_PICK_UP:
                continue
            self.items.append(item)
            yield from self.crawler.emit(f"take {item}")

    def move_to(self, pos):
        commands = dijkstra(self.graph, self.pos, pos)
        for command in commands:
            self.last_command = command
            self.last_pos = self.pos
            self.pos = self.graph[self.pos][command]
            yield from self.crawler.emit(command)

    def explore_ship(self):
        to_explore = []
        while True:
            room_str = self.crawler.get_buffered_output()
            # examine_room picks up (non-bad) items
            yield from self.examine_room(room_str)
            for door, next_room in self.graph[self.pos].items():
                if next_room not in self.graph:
                    # store the proximate location of the unknown room,
                    # for prettier printouts when exploring
                    to_explore.append((self.pos, door, next_room))
            if not to_explore:
                print("BOT: exploration done, going to the test location...")
                yield from self.move_to("Security Checkpoint")
                return self.items, self.cmd_to_test
            # pop latest == DFS
            adjacent, door, target = to_explore.pop()
            print(f"BOT: trying room {door} of {adjacent}...")
            yield from self.move_to(target)
            self.pos = target


def dijkstra(graph, start, goal):
    prev = dict()
    dist = defaultdict(lambda: 999999999999999)
    dist[start] = 0
    queue = [(0, start)]
    while queue:
        dist_to_curr, curr = heapq.heappop(queue)
        if curr == goal:
            path = [curr]
            while curr in prev:
                path.append(prev[curr])
                curr = prev[curr]
            path = list(reversed(path))
            return path_to_commands(graph, path)
        for neighb in graph[curr].values():
            if neighb != goal and neighb not in graph:
                continue
            dist_to_neighb = dist_to_curr + 1
            if dist_to_neighb < dist[neighb]:
                dist[neighb] = dist_to_neighb
                prev[neighb] = curr
                heapq.heappush(queue, (dist_to_neighb, neighb))
    havoc = ValueError("grrr")
    raise havoc


def path_to_commands(graph, path):
    return [
        next(door for (door, room) in graph[fr].items() if room == to)
        for (fr, to) in zip(path, path[1:])
    ]


def parse_room(room_str):
    room_str = room_str.strip()
    in_doors = False
    in_items = False
    doors = []
    items = []
    for line in room_str.splitlines():
        line = line.strip()
        if m := re.match("== (?P<name>.*) ==$", line):
            name = m.group("name")
            # due to the way outputs are ignored when traversing multiple
            # doors to get to a certain place, sometimes this function gets
            # multiple room descriptions, thus these calls to .clear().
            doors.clear()
            items.clear()
            in_doors = False
            in_items = False
            continue
        if line == "Doors here lead:":
            in_doors = True
            in_items = False
            continue
        if line == "Items here:":
            in_doors = False
            in_items = True
            continue
        if m := re.match("- (.*)$", line):
            if in_doors:
                doors.append(m[1])
            elif in_items:
                items.append(m[1])
    return name, doors, items


def part1(opcodes):
    crawler = Crawler(opcodes)
    return crawler.play()


BAD_THINGS_DO_NOT_PICK_UP = [
    "infinite loop",
    "escape pod",
    "molten lava",
    "giant electromagnet",
    "photons",
]


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
