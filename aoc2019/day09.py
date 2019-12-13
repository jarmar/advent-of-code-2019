#!/usr/bin/env python

from collections import defaultdict, namedtuple, deque
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
        prefixes = ["$", "", "~"]
        return f"{prefixes[self.mode]}{self.arg}"


class Computer(object):
    def __init__(self, mem, inp=None, name=None):
        """A computer.

        mem should be a list representing memory (i.e. opcodes).
        inp should be an iterator returning ints.
        """
        self.pc = 0
        self.relbase = 0
        # support virtual memory by the easiest means possible: just make
        # memory lookups in a hashtable defaulting to zero for unknown keys.
        # this should be pretty slow, but fast enough: part 2 takes less than
        # 2 seconds on my machine.
        self.mem = defaultdict(int, {ix: val for ix, val in enumerate(mem)})
        self.inp = inp if inp is not None else iter(())
        self.name = name if name is not None else ""  # for debugging

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
        elif oper.mode == 2:
            return self.mem[oper.arg + self.relbase]
        else:
            raise ValueError(f"bad mode {oper.mode}")

    def get_addr(self, oper):
        if oper.mode == 0:
            return oper.arg
        elif oper.mode == 1:
            raise ValueError("get_addr immediate mode")
        elif oper.mode == 2:
            return oper.arg + self.relbase
        else:
            raise ValueError(f"bad mode {oper.mode}")

    def exec_binop(self, binop, operands):
        arg1 = self.get_argval(operands[0])
        arg2 = self.get_argval(operands[1])
        dst = self.get_addr(operands[2])
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
            dst = self.get_addr(opers[0])
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
        elif op == 9:
            # adjust relative base
            val = self.get_argval(opers[0])
            self.relbase += val
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
    elif op == 9:
        return 1
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
    elif op == 9:
        return "rel"
    elif op == 99:
        return "hlt"
    else:
        return str(op)


def print_program(opcodes):
    opcodes = deque(opcodes)
    full_len = len(opcodes)
    while opcodes:
        offset = full_len - len(opcodes)
        fullop = opcodes.popleft()
        op, modes = parse_fullop(fullop)
        opers = [Operand(opcodes.popleft(), mode) for mode in modes]
        print(
            f"{offset:>3}: {op_to_str(op)} "
            + " ".join(str(oper) for oper in opers)
        )


def part1(opcodes):
    com = Computer(opcodes, inp=iter([1]))
    return list(com.run())[-1]


def part2(opcodes):
    com = Computer(opcodes, inp=iter([2]))
    return list(com.run())[-1]


# fmt: off
def test1():
    t1 = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
    com1 = Computer(t1)
    assert list(com1.run()) == t1

    t2 = [1102, 34915192, 34915192, 7, 4, 7, 99, 0]
    com2 = Computer(t2)
    out2 = list(com2.run())
    assert len(out2) == 1
    assert len(str(out2[0])) == 16

    t3 = [104, 1125899906842624, 99]
    com3 = Computer(t3)
    out3 = list(com3.run())
    assert len(out3) == 1
    assert out3[0] == t3[1]
# fmt: on


if __name__ == "__main__":
    test1()
    with open(sys.argv[1]) as f:
        contents = f.read()
    opcodes = [int(opcode) for opcode in contents.strip().split(",")]
    # print_program(opcodes)

    print(f"part 1: {part1(opcodes)}")
    print(f"part 2: {part2(opcodes)}")
