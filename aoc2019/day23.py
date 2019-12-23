#!/usr/bin/env python

import code
import cProfile as profile
from collections import defaultdict, namedtuple, deque
from itertools import chain, product
import itertools
import re
import sys

from aoc2019.intcode import Computer


GLOBAL_TIMER = 0


Packet = namedtuple("Packet", ["x", "y"])


class PacketQueue:
    def __init__(self):
        self.queue = deque()
        self.last_get = GLOBAL_TIMER

    def get(self):
        while True:
            self.last_get = GLOBAL_TIMER
            if self.queue:
                packet = self.queue.popleft()
                yield packet.x
                yield packet.y
            else:
                yield -1


def setup_network(opcodes):
    inputs = [PacketQueue() for ix in range(50)]
    outputs = [list() for _ in range(50)]
    coms = [
        Computer(opcodes, inp=chain([ix], inputs[ix].get()))
        for ix in range(50)
    ]
    # use slowly=True to be able to run all computers in instruction-level
    # synchronization.
    runs = [com.run(slowly=True) for com in coms]
    return inputs, outputs, runs


def part1(opcodes):
    inputs, outputs, runs = setup_network(opcodes)
    while True:
        # step once
        for ix, run in enumerate(runs):
            out = next(run)
            if out is not None:
                outputs[ix].append(out)
        # collect any new packets
        for output in outputs:
            if len(output) == 3:
                addr = output[0]
                packet = Packet(output[1], output[2])
                if addr == 255:
                    return packet.y
                inputs[addr].queue.append(packet)
                output.clear()


def part2(opcodes):
    global GLOBAL_TIMER
    inputs, outputs, runs = setup_network(opcodes)
    last_send = GLOBAL_TIMER
    prev_nat_y = None
    nat_packet = None
    while True:
        GLOBAL_TIMER += 1
        # step once
        for ix, run in enumerate(runs):
            out = next(run)
            if out is not None:
                outputs[ix].append(out)
        # collect any new packets
        for output in outputs:
            if len(output) == 3:
                last_send = GLOBAL_TIMER
                addr = output[0]
                packet = Packet(output[1], output[2])
                if addr == 255:
                    nat_packet = packet
                else:
                    inputs[addr].queue.append(packet)
                output.clear()
        # are we idle?
        if nat_packet is not None and all(
            (not queue.queue and queue.last_get > last_send)
            for queue in inputs
        ):
            # the solution is so slow, so this print is included to ensure the
            # user that something's actually happening.
            print(f"sending NAT y: {nat_packet.y}")
            last_send = GLOBAL_TIMER
            if nat_packet.y == prev_nat_y:
                return nat_packet.y
            inputs[0].queue.append(nat_packet)
            prev_nat_y = nat_packet.y
            nat_packet = None


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        opcodes = [int(o) for o in f.read().strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
