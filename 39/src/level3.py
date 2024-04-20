from __future__ import annotations

from collections import Counter
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

dirs = {"W": Vec(0,-1), "S": Vec(0,1), "A": Vec(-1,0), "D": Vec(1,0)}


def run_level(infile: str, input: List[str], outfile: str) -> str:
    i = 1
    res = ""
    while i < len(input):
        width, height = Vec(*map(int, input[i].split(' ')))
        mapp = {Vec(x,y): input[i+1+y][x] for x in range(width) for y in range(height)}
        path = input[i+height+1].strip()
        i += height + 2
        res += f"{run_yard(mapp, path)}\n"
    return res[:-1]


def run_yard(mapp, path):
    pass
    poss = [Vec(0,0)] + list(accumulate((dirs[l] for l in path), operator.add))
    mins = Vec(*map(min, zip(*poss)))
    poss = [p-mins for p in poss]
    if max(Counter(poss).values()) == 1 and all(c in poss for c, t in mapp.items() if t == '.') and all(mapp.get(p, '#') == '.' for p in poss):
        return 'VALID'
    return 'INVALID'



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
