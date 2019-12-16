#!/usr/bin/env python

from itertools import chain, cycle, repeat
import sys


def coefficients(ix):
    # very cool and very pythonic
    gen = cycle(
        chain(repeat(0, ix), repeat(1, ix), repeat(0, ix), repeat(-1, ix))
    )
    next(gen)  # throw one away
    yield from gen


def part1_step(msg_list):
    for ix in range(len(msg_list)):
        # fast and loose: modify in-place, since for ix i, the coefficient is
        # zero for all indicies < i, so it doesn't matter that we already
        # modified earlier digits.
        msg_list[ix] = (
            abs(sum(c * k for (c, k) in zip(coefficients(ix + 1), msg_list)))
            % 10
        )


def part1(message):
    message = [int(n) for n in message]
    for i in range(100):
        part1_step(message)
    return "".join(str(i) for i in message[:8])


def part2_step(msg_list):
    # offset > n_relevant_digits, which means that for digit i, the coefficient
    # is 1 for all digits after it. in other words:
    #     digit'[i] = (digit[i] + digit[i+1] + ... + digit[-1]) % 10
    #     (for the last digit, digit'[i] = digit[i] % 10 = digit[i])
    # by elimination of common expressions:
    #     digit'[i] = (digit[i] + digit'[i+1]) % 10
    # ...since each digit only depends on the digits after it, we can modify
    # the list in-place, starting from the next-to-last digit.
    for ix in reversed(range(len(msg_list) - 1)):
        msg_list[ix] = (msg_list[ix] + msg_list[ix + 1]) % 10


def part2(message):
    msg_len = len(message)
    offset = int(message[:7])
    message = [int(n) for n in message]
    # for digits at the offset and onward, earlier digits have coefficient zero
    # and can be ignored (can be seen in matrices on problem page).
    n_relevant_digits = msg_len * 10000 - offset
    n_full_cycles = n_relevant_digits // msg_len
    additional = n_relevant_digits % msg_len

    reduced_msg = message[-additional:] + message * n_full_cycles
    assert len(reduced_msg) == n_relevant_digits

    # do the thing
    for i in range(100):
        part2_step(reduced_msg)
    return "".join(str(i) for i in reduced_msg[:8])


def test1():
    l = [1, 2, 3, 4, 5, 6, 7, 8]
    part1_step(l)
    assert [4, 8, 2, 2, 6, 1, 5, 8] == l
    part1_step(l)
    assert [3, 4, 0, 4, 0, 4, 3, 8] == l
    assert "24176176" == part1("80871224585914546619083218645595")


def test2():
    assert "84462026" == part2("03036732577212944063491565474664")


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        message = f.read().strip()

    print(f"part 1: {part1(message)}")
    print(f"part 2: {part2(message)}")
