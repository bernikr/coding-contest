from __future__ import annotations

from functools import reduce
from itertools import accumulate
import math
import operator
import os
from typing import List

class Vec(tuple[int, ...]):
    def __new__(cls, *args: int | float) -> Vec:
        return super().__new__(cls, args)

    def __add__(self, other):
        return Vec(*map(operator.add, self, other))

    def __sub__(self, other):
        return Vec(*map(operator.sub, self, other))

    def __mul__(self, other):
        if isinstance(other, int | float):
            return Vec(*map(lambda x: x * other, self))
        else:
            raise NotImplemented

    def __truediv__(self, other):
        if isinstance(other, int | float):
            return Vec(*map(lambda x: x // other if x % other == 0 else x / other, self))
        else:
            raise NotImplemented

    def manhatten(self):
        return sum(abs(x) for x in self)

class Box:
    def __init__(self, *corners):
        corners = [tuple(c) for c in corners]
        self.lower = Vec(*map(min, zip(*corners)))
        self.upper = Vec(*map(max, zip(*corners)))

    @classmethod
    def empty(cls, dim):
        b = cls()
        b.lower = Vec(*(math.inf,) * dim)
        b.upper = Vec(*(-math.inf,) * dim)
        return b

    def __contains__(self, item):
        return all(mi <= i <= ma for mi, ma, i in zip(self.lower, self.upper, item))

    def __repr__(self):
        return f"Box{{{self.lower}...{self.upper}}}"

    def overlaps(self, other):
        return all(sl <= ol <= su or sl <= ou <= su or ol <= sl <= ou or ol <= su <= ou
                   for sl, su, ol, ou in zip(self.lower, self.upper, other.lower, other.upper))

    def is_empty(self):
        return all(sl == math.inf and su == -math.inf for sl, su in zip(self.lower, self.upper))

    def __and__(self, other):
        if isinstance(other, Box):
            if self.overlaps(other):
                return Box(map(max, zip(self.lower, other.lower)), map(min, zip(self.upper, other.upper)))
            else:
                return Box.empty(len(self.lower))
        else:
            raise NotImplementedError()

    def size(self):
        return reduce(operator.mul, map(lambda l, u: u - l + 1, self.lower, self.upper))


dirs = {"W": Vec(0,-1), "S": Vec(0,1), "A": Vec(-1,0), "D": Vec(1,0)}


def run_level(infile: str, input: List[str], outfile: str) -> str:
    return '\n'.join(run_line(l.strip()) for l in input[1:])


def run_line(line):
    poss = list(accumulate((dirs[l] for l in line), operator.add))
    bbox = Box(*poss)
    s = tuple(map(lambda l, u: u - l + 1, bbox.lower, bbox.upper))
    return f"{s[0]} {s[1]}"

#####################################

def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')


def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'


if __name__ == '__main__':
    level = os.path.basename(__file__).split('.py')[0]
    print(os.getcwd())

    leveldir = os.path.join(os.path.dirname(__file__), '../levels/' + level + '/')
    for file in os.listdir(leveldir):
        infile = leveldir + file

        if not is_input_file(infile):
            continue

        with open(infile) as f:
            content = f.readlines()

        outfile = get_outfile(infile)
        result = run_level(infile, content, outfile)

        if result and len(result) > 0:
            with open(outfile, 'w') as f:
                f.write(result)
                f.write('\n')
