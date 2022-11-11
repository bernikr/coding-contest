from __future__ import annotations

import operator
import os
from enum import Enum
from heapq import heappush, heappop
from itertools import *
import random
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
    'L': Dir.LEFT,
    'R': Dir.RIGHT,
    'D': Dir.DOWN,
}

class PriorityQueue:
    def __init__(self):
        self.items = []
        self.queue = []

    def __len__(self):
        return len(self.queue)

    def put(self, item, priority):
        self.items.append(item)
        heappush(self.queue, (priority, len(self.items) - 1))

    def get(self):
        return self.items[heappop(self.queue)[1]]


def run_level(infile: str, input: List[str], outfile: str) -> str:
    board_size = int(input[0])
    board = {(x + 1, y + 1): input[x + 1][y] for x in range(board_size) for y in range(board_size)}
    pac_start = Vec(*map(int, input[board_size + 1].split(' ')))
    max_length = int(input[-1])
    res = False
    while not res:
        res = random_path(pac_start, board, max_length)
    return res


def random_path(start, board, max_length):
    coins = set(c for c, v in board.items() if v == "C")
    path = ""
    pos = start
    last_dir = Vec(0, 0)
    while coins:
        possible_dirs = [(d_str, d) for d_str, d in dir_map.items()
                         if board[pos + d.value] not in ["W", "G"] and d.value != last_dir*-1]
        if not possible_dirs:
            possible_dirs = [(d_str, d) for d_str, d in dir_map.items()
                             if board[pos + d.value] not in ["W", "G"]]
        random.shuffle(possible_dirs)
        d_str, d = possible_dirs[0]
        pos += d.value
        coins = coins.difference({pos})
        path += d_str
        last_dir = d.value
        if len(path) > max_length:
            return False
    return path

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
