#!/usr/bin/env python

import re
import sys


def perform_instr(deck, instr):
    if re.match("deal into new stack$", instr):
        deck.reverse()
        return deck
    elif match := re.match("deal with increment (.*)$", instr):
        increment = int(match[1])
        new_deck = [None] * len(deck)
        for ix, card in enumerate(deck):
            new_deck[(ix * increment) % len(deck)] = card
        return new_deck
    elif match := re.match("cut (.*)$", instr):
        cut = int(match[1])
        return deck[cut:] + deck[:cut]
    else:
        raise ValueError(f"unparsable instruction {instr}")


def do_instructions(deck, instructions):
    for instr in instructions:
        deck = perform_instr(deck, instr)
    return deck


def part1(instructions):
    deck = list(range(10007))
    deck = do_instructions(deck, instructions)
    return deck.index(2019)


def euclid_wallis(mod, num):
    # requires gcd(mod, num) == 1?
    # calculates k such that (k * num) % mod == 1
    lcol = [1, 0, mod]
    rcol = [0, 1, num]
    while rcol[2] != 0:
        above = lcol[2] // rcol[2]
        new_col = [l - r * above for (l, r) in zip(lcol, rcol)]
        lcol = rcol
        rcol = new_col
    return lcol[1] % mod


def perform_instr_backwards(deck_len, instr):
    if re.match("deal into new stack$", instr):
        yield ("add", 1)
        yield ("mul", -1)
    elif match := re.match("deal with increment (.*)$", instr):
        increment = int(match[1])
        #   after = (increment * before) % deck_len
        # (note: we're shuffling backwards, i.e. going from "after" to "before")
        # want to find m such that (m * increment) % deck_len == 1, i.e.:
        #   m * after = (m * increment * before) % deck_len
        #   m * after = before % deck_len
        multiplier = euclid_wallis(deck_len, increment)
        yield ("mul", multiplier)
    elif match := re.match("cut (.*)$", instr):
        cut = int(match[1])
        yield ("add", cut)
    else:
        raise ValueError(f"unparsable instruction {instr}")


def do_backwards(deck_ix, deck_len, iterations, instructions):
    # all shuffling instructions can be expressed as modular addition or
    # multiplication. actually applying the modulo can be deferred as desired.
    xs = 1
    ones = 0
    for instr in reversed(instructions):
        for op, val in perform_instr_backwards(deck_len, instr):
            if op == "add":
                ones += val
            elif op == "mul":
                xs *= val
                ones *= val
    # the result is given by repeatedly applying, "iterations" times:
    #   x * xs + ones
    # (where x initially equals deck_ix)
    # let I = iterations, then the result of the repeated application is
    # given by:
    #   deck_ix * xs^I + (1 + xs + xs² + ... + xs^(I - 1)) * ones
    # (all modulo deck_len)
    # the parenthesized expression is a geometric series, which can be
    # efficiently calculated using the "repeated squaring" method.
    total_xs = pow(xs, iterations, deck_len)
    geo = geosum(xs, iterations - 1, deck_len)
    return (deck_ix * total_xs + geo * ones) % deck_len


def geosum(a, n, mod):
    # using repeated squaring, calculates the value of:
    #  (1 + a + a^2 + ... + a^n) % mod
    if n == 0:
        return 1
    # let n == 2m + 1:
    #     (1 + a + a² + ... + a^(2m + 1)) % mod
    #  == (a + 1) * (1 + a² + (a²)² + ... + (a²)^m) % mod
    # note that `n // 2` discards the last bit, so if n is even, the right
    # hand side (i.e. "result") will have an extra a^(n + 1) term which needs
    # subtracting.
    a2 = (a * a) % mod
    result = (a + 1) * geosum(a2, n // 2, mod)
    if n % 2 == 1:
        return result % mod
    else:
        return (result - pow(a, n + 1, mod)) % mod


def part2(instructions):
    card = 2020
    deck_len = 119315717514047
    iterations = 101741582076661
    return do_backwards(card, deck_len, iterations, instructions)


TEST_0 = """\
deal with increment 7
deal into new stack
deal into new stack
"""


TEST_1 = """\
cut 6
deal with increment 7
deal into new stack
"""


TEST_2 = """\
deal with increment 7
deal with increment 9
cut -2
"""


TEST_3 = """\
deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1
"""


def test1_case(instrs_str, expected):
    deck = list(range(10))
    deck = do_instructions(deck, instrs_str.splitlines())
    if deck != expected:
        print(f"deck:      {deck}")
        print(f"expected:  {expected}")
    assert expected == deck


TEST_0_EXPECTED = [0, 3, 6, 9, 2, 5, 8, 1, 4, 7]
TEST_1_EXPECTED = [3, 0, 7, 4, 1, 8, 5, 2, 9, 6]
TEST_2_EXPECTED = [6, 3, 0, 7, 4, 1, 8, 5, 2, 9]
TEST_3_EXPECTED = [9, 2, 5, 8, 1, 4, 7, 0, 3, 6]


def test1():
    test1_case(TEST_0, TEST_0_EXPECTED)
    test1_case(TEST_1, TEST_1_EXPECTED)
    test1_case(TEST_2, TEST_2_EXPECTED)
    test1_case(TEST_3, TEST_3_EXPECTED)


def test2_case(instrs_str, expected):
    # these test cases don't test the actually tricky parts, since they only
    # use a single iteration....
    for ix, card in enumerate(expected):
        assert card == do_backwards(ix, 10, 1, instrs_str.splitlines())


def test2():
    assert euclid_wallis(26, 7) == 15
    test2_case(TEST_0, TEST_0_EXPECTED)
    test2_case(TEST_1, TEST_1_EXPECTED)
    test2_case(TEST_2, TEST_2_EXPECTED)
    test2_case(TEST_3, TEST_3_EXPECTED)


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        instructions = f.readlines()

    print(f"part 1: {part1(instructions)}")
    print(f"part 2: {part2(instructions)}")
