#!/usr/bin/env python

from collections import namedtuple, deque
from itertools import product, repeat, permutations, chain, tee
import sys
import operator


# Used similar to the built-in StopIteration.
class StOp99(Exception):
    pass


class Operand(object):
    def __init__(self, arg, mode):
        self.arg = arg
        self.mode = mode

    def __str__(self):
        prefixes = ["$", "#"]
        return f"{prefixes[self.mode]}{self.arg}"


class Computer(object):
    def __init__(self, name, mem, inp):
        """A computer.

        mem should be a list representing memory (i.e. opcodes).
        inp should be an iterator returning ints.
        """
        self.pc = 0
        self.name = name  # for debugging
        self.mem = list(mem)  # avoid headaches
        self.inp = inp

    def run(self):
        """Run the program, yielding the results of output instructions."""
        while True:
            fullop = self.get()
            op, modes = parse_fullop(fullop)
            opers = [Operand(self.get(), mode) for mode in modes]
            try:
                result = self.exec_op(op, opers)
                if result is not None:
                    yield result
            except StOp99:
                break

    def get(self):
        val = self.mem[self.pc]
        self.pc += 1
        return val

    def get_argval(self, oper):
        if oper.mode == 0:
            return self.mem[oper.arg]
        elif oper.mode == 1:
            return oper.arg
        else:
            raise ValueError(f"bad mode {oper.mode}")

    def exec_binop(self, binop, opers):
        arg1 = self.get_argval(opers[0])
        arg2 = self.get_argval(opers[1])
        dst = opers[2].arg  # always position mode
        self.mem[dst] = int(binop(arg1, arg2))

    def exec_op(self, op, opers):
        if op == 1:
            # add
            self.exec_binop(operator.add, opers)
        elif op == 2:
            # multiply
            self.exec_binop(operator.mul, opers)
        elif op == 3:
            # input
            val = next(self.inp)
            dst = opers[0].arg  # always position mode
            self.mem[dst] = val
        elif op == 4:
            # output
            val = self.get_argval(opers[0])
            return val
        elif op == 5:
            # jump-if-true
            val = self.get_argval(opers[0])
            jmp_to = self.get_argval(opers[1])
            if val:
                self.pc = jmp_to
        elif op == 6:
            # jump-if-false
            val = self.get_argval(opers[0])
            jmp_to = self.get_argval(opers[1])
            if not val:
                self.pc = jmp_to
        elif op == 7:
            # less than
            self.exec_binop(operator.lt, opers)
        elif op == 8:
            # equals
            self.exec_binop(operator.eq, opers)
        elif op == 99:
            raise StOp99()
        else:
            raise ValueError(f"exec_op bad op {op}")


def op_arglen(op):
    if op == 1:
        return 3
    elif op == 2:
        return 3
    elif op == 3:
        return 1
    elif op == 4:
        return 1
    elif op == 5:
        return 2
    elif op == 6:
        return 2
    elif op == 7:
        return 3
    elif op == 8:
        return 3
    elif op == 99:
        return 0
    else:
        return 0


def parse_fullop(fullop):
    op = fullop % 100
    fullop //= 100
    arglen = op_arglen(op)
    modes = []
    for _ in range(arglen):
        modes.append(fullop % 10)
        fullop //= 10
    return op, modes


# For debugging purposes.
def op_to_str(op):
    if op == 1:
        return "add"
    elif op == 2:
        return "mul"
    elif op == 3:
        return "inp"
    elif op == 4:
        return "out"
    elif op == 5:
        return "jt "
    elif op == 6:
        return "jf "
    elif op == 7:
        return "lt "
    elif op == 8:
        return "eq "
    elif op == 99:
        return "hlt"
    else:
        return str(op)


def print_program(opcodes):
    opcodes = deque(opcodes)
    while opcodes:
        fullop = opcodes.popleft()
        op, modes = parse_fullop(fullop)
        opers = [Operand(opcodes.popleft(), mode) for mode in modes]
        print(f"{op_to_str(op)} " + " ".join(str(oper) for oper in opers))


def part1(opcodes):
    results = []
    for phases in permutations(range(5)):
        computers = []
        for phase in phases:
            if computers:
                prev_outp = computers[-1].run()
                inp = chain(iter([phase]), prev_outp)
            else:
                inp = iter([phase, 0])
            computers.append(Computer(len(computers), opcodes, inp=inp))
        result = int("".join(str(i) for i in computers[-1].run()))
        results.append(result)
    return max(results)


class LazyChain(object):
    """After-the-fact manipulable itertools.chain.

    Like itertools.chain, but allowing us to put more stuff in after its
    creation, by exposing the list (deque) of generators to yield from.
    """

    def __init__(self, it):
        self.iters = deque([it])

    def run(self):
        while self.iters:
            it = self.iters.popleft()
            yield from it


def part2(opcodes):
    results = []
    for phases in permutations(range(5, 10)):
        computers = []
        for phase in phases:
            if computers:
                prev_outp = computers[-1].run()
                inp = chain(iter([phase]), prev_outp)
            else:
                # Save it so we can attach the last computer later on
                first_gen = LazyChain(iter([phase, 0]))
                inp = first_gen.run()
            computers.append(Computer(len(computers), opcodes, inp=inp))
        # Split the output from the last computer...
        last_out = computers[-1].run()
        first_inp, result_out = tee(last_out)
        # ...connect one as input to the first computer...
        first_gen.iters.append(first_inp)
        # ...get the last item from the other one as our final result.
        result = list(result_out)[-1]
        results.append(result)
    return max(results)


# fmt: off
def test1():
    assert 43210 == part1(
        [3, 15, 3, 16, 1002, 16, 10, 16, 1, 16, 15, 15, 4, 15, 99, 0, 0]
    )
    assert 54321 == part1(
        [
            3, 23, 3, 24, 1002, 24, 10, 24, 1002, 23, -1, 23, 101, 5, 23, 23,
            1, 24, 23, 23, 4, 23, 99, 0, 0
        ]
    )
    assert 65210 == part1(
        [
            3, 31, 3, 32, 1002, 32, 10, 32, 1001, 31, -2, 31, 1007, 31, 0, 33,
            1002, 33, 7, 33, 1, 33, 31, 31, 1, 32, 31, 31, 4, 31, 99, 0, 0, 0
        ]
    )


def test2():
    assert 139629729 == part2(
        [
            3, 26, 1001, 26, -4, 26, 3, 27, 1002, 27, 2, 27, 1, 27, 26, 27, 4,
            27, 1001, 28, -1, 28, 1005, 28, 6, 99, 0, 0, 5
        ]
    )
    assert 18216 == part2(
        [
            3, 52, 1001, 52, -5, 52, 3, 53, 1, 52, 56, 54, 1007, 54, 5, 55,
            1005, 55, 26, 1001, 54, -5, 54, 1105, 1, 12, 1, 53, 54, 53, 1008,
            54, 0, 55, 1001, 55, 1, 55, 2, 53, 55, 53, 4, 53, 1001, 56, -1,
            56, 1005, 56, 6, 99, 0, 0, 0, 0, 10
        ]
    )
# fmt: on


if __name__ == "__main__":
    test1()
    test2()
    with open(sys.argv[1]) as f:
        contents = f.read()
    opcodes = [int(opcode) for opcode in contents.strip().split(",")]

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
