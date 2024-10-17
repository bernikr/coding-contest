from __future__ import annotations

import re
from itertools import count, repeat
from typing import List, Iterator


##################################################


def split_input(inp: List[str]) -> Iterator[tuple]:
    for line in inp:
        yield (line,)  # output tuple will be input params of solve and validate method


def solve(line) -> str:
    return str(len(line))


def validate(solution: str, line) -> bool:
    return True


##################################################
WORKERS = 1
RECOMPUTE = False
CACHING = True
##################################################

import filecmp  # noqa: E402
import functools  # noqa: E402
import inspect  # noqa: E402
import multiprocessing  # noqa: E402
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
                tasks = [
                    executor.submit(_solve_worker, inp, stopping_event)
                    for _ in range(WORKERS)
                ]
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
    results = list(cmap(_solve_cached, preprocessed_input, count(), repeat(outfile)))

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
        if filecmp.cmp(
            example_in_file.with_suffix(".out"),
            example_in_file.with_suffix(".out.computed"),
        ):
            print("✅ Example check passed")
        else:
            print("⚠️ Example check failed")

    for file in leveldir.iterdir():
        if re.match(r"level\d+_\d+\.in", file.name):
            _run_file(file, file.with_suffix(".out"))


if __name__ == "__main__":
    _main()
