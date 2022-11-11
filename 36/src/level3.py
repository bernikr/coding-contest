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
    board = {(x + 1, y + 1): input[x + 1][y] for x in range(board_size) for y in range(board_size)}
    pac_start = Vec(*map(int, input[board_size + 1].split(' ')))
    pac_moves = [dir_map[c] for c in input[board_size + 3].strip()]

    num_ghosts = int(input[board_size + 4])
    ghost_start = [Vec(*map(int, input[board_size + 5 + i * 3].split(' '))) for i in range(num_ghosts)]
    ghost_moves = [[dir_map[c] for c in input[board_size + 7 + i * 3].strip()] for i in range(num_ghosts)]

    pac_pos = pac_start
    ghost_pos = ghost_start
    coin_count = 0
    collected_coins = []
    alive = True
    for i in range(len(pac_moves)):
        pac_pos += pac_moves[i].value
        ghost_pos = [g + ghost_moves[gi][i].value for g, gi in zip(ghost_pos, range(num_ghosts))]

        if board[pac_pos] == 'W':
            alive = False
            break

        if any(pac_pos == p for p in ghost_pos):
            alive = False
            break

        if board[pac_pos] == 'C' and pac_pos not in collected_coins:
            collected_coins.append(pac_pos)
            coin_count += 1

    return f"{len(collected_coins)} {'YES' if alive else 'NO'}"


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
