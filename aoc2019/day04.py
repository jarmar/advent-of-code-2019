#!/usr/bin/env python


def adjacent_equal(s):
    return (
        s[0] == s[1]
        or s[1] == s[2]
        or s[2] == s[3]
        or s[3] == s[4]
        or s[4] == s[5]
    )


def exactly_two_adjacent_equal(s):
    return (
        s[0] == s[1] != s[2]
        or s[0] != s[1] == s[2] != s[3]
        or s[1] != s[2] == s[3] != s[4]
        or s[2] != s[3] == s[4] != s[5]
        or s[3] != s[4] == s[5]
    )


def no_decrease(s):
    return s[0] <= s[1] <= s[2] <= s[3] <= s[4] <= s[5]


def part1(lower, upper):
    count = 0
    for i in range(lower, upper + 1):
        s = str(i)
        if no_decrease(s) and adjacent_equal(s):
            count += 1
    return count


def part2(lower, upper):
    count = 0
    for i in range(lower, upper + 1):
        s = str(i)
        if no_decrease(s) and exactly_two_adjacent_equal(s):
            count += 1
    return count


if __name__ == "__main__":
    lower = 165432
    upper = 707912
    print(f"part 1: {part1(lower, upper)}")
    print(f"part 2: {part2(lower, upper)}")
