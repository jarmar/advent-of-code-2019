#!/usr/bin/env python

import itertools
import sys

import aoc2019.utils as utils


def read_layers(data, width, height):
    layer_size = width * height
    return [
        list(utils.chunks(layer, width))
        for layer in utils.chunks(data, layer_size)
    ]


def count_num(num, layer):
    return len([px for px in itertools.chain(*layer) if px == num])


def count_zeroes(layer):
    return count_num(0, layer)


def part1(data):
    layers = read_layers(data, 25, 6)
    the_layer = min(layers, key=count_zeroes)
    ones = count_num(1, the_layer)
    twos = count_num(2, the_layer)
    return ones * twos


def part2(data):
    layers = read_layers(data, 25, 6)
    output = [
        # (read bottom-up)
        [
            # Use the first non-transparent value
            next(px for px in px_layers if px != 2)
            # px_layers == all layers for a given pixel
            for px_layers in zip(*row_layers)
        ]
        # row_layers == all layers for a given row
        for row_layers in zip(*layers)
    ]
    # map 0 => "░", 1 => "█"
    return "\n".join("".join("░█"[px] for px in row) for row in output)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = f.read()
    data = [int(ch) for ch in data.strip()]
    print(f"part 1: {part1(data)}")
    print(f"part 2:\n{part2(data)}")
