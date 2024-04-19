from __future__ import annotations

import operator
import os
from enum import Enum
from itertools import *
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
dirs8 = [Vec(*c) for c in product([-1, 0, 1], repeat=2) if c != (0, 0)]


class Dir(Enum):
    UP = Vec(-1, 0)
    DOWN = Vec(1, 0)
    LEFT = Vec(0, -1)
    RIGHT = Vec(0, 1)

    def turn_left(self):
        return Dir((self.value[1], -self.value[0]))

    def turn_right(self):
        return Dir((-self.value[1], self.value[0]))

dir_map = {
    'U': Dir.UP,
    'D': Dir.DOWN,
    'L': Dir.LEFT,
    'R': Dir.RIGHT
}


def run_level(infile: str, input: List[str], outfile: str) -> str:
    board_size = int(input[0])
    board = {(x+1, y+1): input[x+1][y] for x in range(board_size) for y in range(board_size)}
    start = Vec(*map(int, input[board_size + 1].split(' ')))
    movement = [dir_map[c] for c in input[-1].strip()]
    pacman_coords = set(accumulate(map(operator.attrgetter("value"), movement), initial=start))
    #return str(pacman_coords)
    return str(sum(1 for c in pacman_coords if board[c] == "C"))


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
