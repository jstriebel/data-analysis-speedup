import functools
import sys
from os import getpid
from subprocess import DEVNULL, Popen
from time import perf_counter, process_time, sleep

from IPython.display import FileLink, display


def reset_measure_and_compare():
    global timing
    timing = {}


reset_measure_and_compare()


def measure_and_compare(max_time=15):
    def decorator(func):
        version = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if "max_time" in kwargs:
                current_max_time = kwargs.pop("max_time")
            else:
                current_max_time = max_time

            args_string = ",".join(map(str, args))
            if args_string.endswith("small"):
                return func(*args, **kwargs)
            svg_path = f"profiles/{version}__{args_string.replace('/', '_')}.svg"
            py_spy_process = Popen(
                [
                    "py-spy",
                    "record",
                    "--native",
                    "--subprocesses",
                    "--nolineno",
                    "-o",
                    svg_path,
                    "-d",
                    str(current_max_time),
                    "--pid",
                    str(getpid()),
                ],
                stdout=DEVNULL,
            )

            wall_start = perf_counter()
            start = process_time()
            result = func(*args, **kwargs)
            end = process_time()
            wall_end = perf_counter()

            wall_time = wall_end - wall_start

            timing_for_args = timing.setdefault(args, {})
            timing_for_args[version] = end - start

            initial_version = next(iter(timing_for_args.keys()))
            if initial_version != version:
                initial_timing = next(iter(timing_for_args.values()))
                x_perc_faster = (initial_timing / timing_for_args[version]) - 1
                print(
                    f"{timing_for_args[version]:5.2f}s ({wall_time:5.2f}s wall) {version}({args_string}), {x_perc_faster:.2%} faster ({initial_version} was {initial_timing:5.2f}s)"
                )
            else:
                print(
                    f"{timing_for_args[version]:5.2f}s ({wall_time:5.2f}s wall)  {version}({args_string})"
                )

            py_spy_process.wait()
            display(FileLink(svg_path))
            return result

        return wrapper

    return decorator
