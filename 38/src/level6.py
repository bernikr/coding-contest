from __future__ import annotations

import operator
import os
import random
from itertools import product, pairwise
from operator import itemgetter
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
dirs8 = [Vec(0, -1), Vec(1, -1), Vec(1, 0), Vec(1, 1), Vec(0, 1), Vec(-1, 1), Vec(-1, 0), Vec(-1, -1)]


def check_route_valid(level, route):
    discovered_tiles = {route[0]}
    discovered_diags = set()
    for prev, cur in pairwise(route):
        if cur in discovered_tiles:
            return False
        discovered_tiles.add(cur)
        if cur + prev in discovered_diags:
            return False
        discovered_diags.add(cur + prev)
    return True


def rotate(dir):
    return dirs8[dirs8.index(dir) - 1]


def step(level, pos, coast):
    assert level[pos] == "W"
    assert level[coast] == "L"
    assert (pos - coast).manhatten() == 1

    candidate = coast + rotate(rotate(pos - coast))
    if level[candidate] == "W":
        return candidate, coast

    candidate2 = coast + rotate(pos - coast)
    if level[candidate2] == "W":
        return candidate2, candidate

    return step(level, pos, candidate2)


def letter(pos, level, path, island):
    if pos == island:
        return "X"
    if pos in path:
        return "#"
    if level[pos] == "L":
        return "."
    return " "


def encircle(level, island):
    starting_pos = island
    while level[starting_pos] == "L":
        coast = starting_pos
        starting_pos += Vec(1, 0)
    pos = starting_pos
    path = [pos]
    while len(path) == 1 or pos != starting_pos:
        prev = pos
        pos, coast = step(level, pos, coast)
        assert level[pos] == "W"
        assert pos - prev in dirs8
        path.append(pos)

    path = path[:-1]
    return path


def find_valid_route(level, a, b):
    ancestors = {}
    next = {a}
    while next:
        current = next
        next = set()
        if b in current:
            break
        for pos in current:
            for d in dirs8:
                if level.get(pos + d, "L") == "W" and pos + d not in ancestors:
                    ancestors[pos + d] = pos
                    next.add(pos + d)
    path = [b]
    while path[-1] != a:
        path.append(ancestors[path[-1]])
    return path[::-1]


def opt(level, path, start, end):
    return path[:start] + find_valid_route(level, path[start], path[end]) + path[end+1:]


def rand_opt(level, path):
    l = len(path)
    new_start = random.randint(0, l)
    path = path[new_start:] + path[:new_start]
    return opt(level, path, l//3, (2*l)//3)


def encircle_opt(level, island):
    path = encircle(level, island)
    l = -1
    while l != len(path):
        l = len(path)
        print(l)
        for i in range(50):
            path = rand_opt(level, path)

    assert path[0] - path[-1] in dirs8
    assert len(path) == len(set(path))
    assert len(path) <= 2 * 250
    assert check_route_valid(level, path)

    size = max(map(itemgetter(0), level.keys()))
    # for y in range(size):
    #    print("".join(letter(Vec(x, y), level, path, island) for x in range(size)))
    print("###")
    assert len(path) >= 4

    return path


def run_level(infile: str, input: List[str], outfile: str) -> str:
    size = int(input[0])
    level = {Vec(x, y): c for y, l in enumerate(input[1:size + 1]) for x, c in enumerate(l)}
    coords = [Vec(*map(int, l.split(","))) for l in input[size + 2:]]
    return "\n".join(" ".join(f"{c[0]},{c[1]}" for c in encircle_opt(level, a)) for a in coords)


#####################################

def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')


def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'


if __name__ == '__main__':
    level = os.path.basename(__file__).split('.py')[0]
    print(os.getcwd())

    leveldir = '../levels/' + level + '/'
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
        print(f"completed {file}")
