#!/usr/bin/env python

from collections import namedtuple
from itertools import product, repeat
import sys
import operator


# Used similar to the built-in StopIteration.
class StOp99(Exception):
    pass


Operand = namedtuple("Operand", ["arg", "mode"])


class Computer(object):
    def __init__(self, mem, inp, outp):
        """A computer.

        mem should be a list representing memory (i.e. opcodes).
        inp should be an iterator returning ints.
        outp should be a function taking a single int as argument.
        """
        self.pc = 0
        self.mem = mem
        self.inp = inp
        self.outp = outp

    def run(self):
        while True:
            fullop = self.get()
            op, modes = parse_fullop(fullop)
            opers = [Operand(self.get(), mode) for mode in modes]
            try:
                self.exec_op(op, opers)
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
            self.outp(val)
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
        raise ValueError(f"bad op {op}")


def parse_fullop(fullop):
    op = fullop % 100
    fullop //= 100
    arglen = op_arglen(op)
    modes = []
    for _ in range(arglen):
        modes.append(fullop % 10)
        fullop //= 10
    return op, modes


def part1(opcodes):
    result = []
    computer = Computer(opcodes, inp=iter([1]), outp=result.append)
    computer.run()
    return "".join(str(i) for i in result)


def part2(opcodes):
    result = []
    computer = Computer(opcodes, inp=iter([5]), outp=result.append)
    computer.run()
    return "".join(str(i) for i in result)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        contents = f.read()
    opcodes = [int(opcode) for opcode in contents.strip().split(",")]

    print(f"part 1: {part1(list(opcodes))}")
    print(f"part 2: {part2(list(opcodes))}")
