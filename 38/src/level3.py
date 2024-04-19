from __future__ import annotations

import itertools
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


dirs4 = [Vec(0, -1), Vec(0, 1), Vec(1, 0), Vec(-1, 0)]


def check_route_valid(level, route):
    discovered_tiles = {route[0]}
    discovered_diags = set()
    for prev, cur in itertools.pairwise(route):
        if cur in discovered_tiles:
            return False
        discovered_tiles.add(cur)
        if cur + prev in discovered_diags:
            return False
        discovered_diags.add(cur + prev)
    return True


def run_level(infile: str, input: List[str], outfile: str) -> str:
    size = int(input[0])
    level = {Vec(x, y): c for y, l in enumerate(input[1:size + 1]) for x, c in enumerate(l)}
    coords = [[Vec(*map(int, a.split(","))) for a in l.split(" ")] for l in input[size + 2:]]
    return "\n".join("VALID" if check_route_valid(level, route) else "INVALID" for route in coords)


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
