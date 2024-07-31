from __future__ import annotations

import operator
import random
from collections import Counter, defaultdict
from itertools import accumulate
from typing import List, Iterator


class Vec(tuple[int, ...]):
    def __new__(cls, *args: int | float):
        if len(args) == 1:
            return super().__new__(cls, *args)
        return super().__new__(cls, args)

    def __add__(self, other):
        return Vec(*map(operator.add, self, other))

    def __sub__(self, other):
        return Vec(*map(operator.sub, self, other))

    def __mul__(self, other):
        if isinstance(other, int | float):
            return Vec(*map(lambda x: x * other, self))
        else:
            raise NotImplementedError

    def __truediv__(self, other):
        if isinstance(other, int | float):
            return Vec(*map(lambda x: x // other if x % other == 0 else x / other, self))
        else:
            raise NotImplementedError

    def manhatten(self):
        return sum(abs(x) for x in self)


class Box:
    def __init__(self, *corners):
        corners = [tuple(c) for c in corners]
        self.lower = Vec(*map(min, zip(*corners)))
        self.upper = Vec(*map(max, zip(*corners)))


dirs = {"W": Vec(0, -1), "A": Vec(-1, 0), "S": Vec(0, 1), "D": Vec(1, 0)}


def split_input(inp: List[str]) -> Iterator[tuple]:
    i = 1
    while i < len(inp):
        width, height = Vec(*map(int, inp[i].split(" ")))
        mapp = {Vec(x, y): inp[i + 1 + y][x] for x in range(width) for y in range(height)}
        i += height + 1
        yield (mapp,)


def solve(mapp) -> str | Iterator[str]:
    mapp = defaultdict(lambda: "#", mapp)
    path = ""
    poss = [[p for p, c in mapp.items() if c == "X"][0] + dirs[random.choice("WASD")]]  # maybe?
    d = random.choice("WASD")
    for i in itertools.count():
        pos = poss[-1]
        opts = [x for x in "WASD" if mapp[pos + dirs[x]] == "." and pos + dirs[x] not in poss]

        if d in opts and not (len(path) > 3 and path[-3] == path[-2] != path[-1]) and mapp[pos + 2 * dirs[d]] == ".":
            path += d
            poss.append(pos + dirs[d])
        else:
            if opts:
                d = random.choice(opts)
                path += d
                poss.append(pos + dirs[d])
            else:
                yield path
                if i < 1000 or i % 2 == 0:
                    poss = [[p for p, c in mapp.items() if c == "X"][0] + dirs[random.choice("WASD")]]
                else:
                    poss = [random.choice([p for p, c in mapp.items() if c == "."])]
                path = ""


def validate(path, mapp) -> bool:
    poss = [Vec(0, 0)] + list(accumulate((dirs[x] for x in path), operator.add))
    mins = Vec(*map(min, zip(*poss)))
    poss = [p - mins for p in poss]
    return max(Counter(poss).values()) == 1 and all(c in poss for c, t in mapp.items() if t == ".") and all(
        mapp.get(p, "#") == "." for p in poss)


##################################################
WORKERS = 32
RECOMPUTE = True
CACHING = True
##################################################

import filecmp  # noqa: E402
import functools  # noqa: E402
import inspect  # noqa: E402
import itertools  # noqa: E402
import multiprocessing  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from concurrent import futures  # noqa: E402
from pathlib import Path  # noqa: E402

from tqdm.contrib import tmap  # noqa: E402
from tqdm.contrib.concurrent import process_map  # noqa: E402

level = Path(__file__).name.split(".py")[0]
leveldir = Path(__file__).parents[1] / "levels" / level
partsdir = leveldir / "parts"
is_trial_and_error = inspect.isgeneratorfunction(solve)


def _solve_worker(inp, stop_event):
    for candidate in solve(*inp):
        if validate(candidate, *inp):
            return candidate
        if stop_event.is_set():
            return None


def _solve(inp, index):
    if not is_trial_and_error:
        res = solve(*inp)
        if not validate(res, *inp):
            print(f"⚠️ Failed to validate part {index}")
        return res
    if WORKERS == 1:
        for candidate in solve(*inp):
            if validate(candidate, *inp):
                return candidate
    else:
        with multiprocessing.Manager() as manager:
            stopping_event = manager.Event()
            with futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
                tasks = [executor.submit(_solve_worker, inp, stopping_event) for _ in range(WORKERS)]
                futures.wait(tasks, return_when=futures.FIRST_COMPLETED)
                res = next(futures.as_completed(tasks)).result()
                stopping_event.set()
        return res


def _solve_cached(inp, index: int, outfile: Path):
    if not CACHING:
        return _solve(inp, index)
    partfile = partsdir / (outfile.name + f".{index}")
    if partfile.exists():
        with partfile.open() as f:
            return f.read()
    else:
        res = _solve(inp, index)
        with partfile.open(mode="w") as f:
            f.write(res)
        return res


def _run_file(infile, outfile):
    with open(leveldir / infile) as f:
        content = f.readlines()

    print(f"{infile.name}")
    preprocessed_input = list(split_input(content))

    if WORKERS > 1 and not is_trial_and_error:
        cmap = functools.partial(process_map, max_workers=WORKERS)
    else:
        cmap = tmap
    cmap = functools.partial(cmap, miniters=1, file=sys.stdout, mininterval=0)
    results = list(cmap(_solve_cached, preprocessed_input, itertools.count(), itertools.repeat(outfile)))

    if results and len(results) > 0:
        with open(leveldir / outfile, "w") as f:
            f.write("\n".join(results))
            f.write("\n")


def _main():
    if CACHING:
        partsdir.mkdir(exist_ok=True)
        if RECOMPUTE:
            for f in partsdir.iterdir():
                f.unlink()

    for file in leveldir.iterdir():
        if re.match(r"level\d+_\d+\.out", file.name):
            file.unlink()

    example_in_file = leveldir / (level + "_example.in")
    if not example_in_file.exists():
        print("⚠️ No example file found")
    else:
        _run_file(example_in_file, example_in_file.with_suffix(".out.computed"))
        if filecmp.cmp(example_in_file.with_suffix(".out"), example_in_file.with_suffix(".out.computed")):
            print("✅ Example check passed")
        else:
            print("⚠️ Example check failed")

    for file in leveldir.iterdir():
        if re.match(r"level\d+_\d+\.in", file.name):
            _run_file(file, file.with_suffix(".out"))


if __name__ == "__main__":
    _main()
