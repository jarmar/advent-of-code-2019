#!/usr/bin/env python

from itertools import product
import sys
import operator


def step(op, in1, in2, out, state):
    state[out] = op(state[in1], state[in2])


def execute(state):
    for i in range(0, len(state), 4):
        opcode = state[i]
        if opcode == 1:
            op = operator.add
        elif opcode == 2:
            op = operator.mul
        else:
            break
        step(op, state[i + 1], state[i + 2], state[i + 3], state)
    return state


def compute_stuff(opcodes, noun, verb):
    opcodes[1] = noun
    opcodes[2] = verb
    return execute(opcodes)[0]


def part1(opcodes):
    return compute_stuff(opcodes, 12, 2)


def part2(opcodes):
    for noun, verb in product(range(99), range(99)):
        if compute_stuff(list(opcodes), noun, verb) == 19690720:
            return 100 * noun + verb
    raise ValueError("forsooth")


def test():
    assert [2, 0, 0, 0, 99] == execute([1, 0, 0, 0, 99])
    assert [2, 3, 0, 6, 99] == execute([2, 3, 0, 3, 99])
    assert [2, 4, 4, 5, 99, 9801] == execute([2, 4, 4, 5, 99, 0])
    assert [30, 1, 1, 4, 2, 5, 6, 0, 99] == execute(
        [1, 1, 1, 4, 99, 5, 6, 0, 99]
    )


if __name__ == "__main__":
    test()

    with open(sys.argv[1]) as f:
        contents = f.read()
    opcodes = [int(opcode) for opcode in contents.strip().split(",")]

    print(f"part 1: {part1(list(opcodes))}")
    print(f"part 2: {part2(list(opcodes))}")
