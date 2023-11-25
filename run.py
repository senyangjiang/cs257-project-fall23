import argparse
import multiprocessing
import os
import datetime
import bisect
from pickle import dump
from pathlib import Path

from common import *
from benchmark import Benchmark
from mk_text_report import create_report

def process(bm):
    return bm.execute()

def find_timeout(path):
    if os.path.exists(os.path.join(path, "TIMEOUT")):
        with open(os.path.join(path, "TIMEOUT"), "rU") as fd:
            tmp = int(fd.read().strip())
            assert tmp > 0
            return tmp
    elif "/" in path:
        return find_timeout("/".join(path.split("/")[:-1]))
    else:
        return None
    
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite",
                    default="test",
                    choices=["test",
                             "smtlib",
                             "anni"])
    ap.add_argument("--single",
                    default=True,
                    action="store_true")
    ap.add_argument("--timeout",
                    default=None,
                    type=int,
                    help="by default we use the benchmark-specific timeout; "
                    "use this option to globally override it")
    ap.add_argument("--force",
                    default=False,
                    action="store_true")
    ap.add_argument("--report",
                    default=False,
                    action="store_true")
    options = ap.parse_args()

    bench_dirs = []
    if options.suite == "test":
        bench_dirs.append("test")
    if options.suite == "smtlib":
        bench_dirs.append("smtlib")
    if options.suite == "anni":
        bench_dirs.append("anni_2022")

    data_filename = f"data_z3_z3.p"

    # Check for existing results; skip this step in --force mode
    EXISTING_RESULTS = set()
    if not options.force:
        Path("results").mkdir(exist_ok=True)
        for group in os.listdir("results"):
            if not os.path.isdir(os.path.join("results", group)):
                continue
            if data_filename in os.listdir(os.path.join("results", group)):
                EXISTING_RESULTS.add(group)

    print("Assembling benchmarks...")
    benchmarks = []
    for d in bench_dirs:
        for path, _, files in os.walk(d):
            timeout = options.timeout
            if timeout is None:
                timeout = find_timeout(path)
            for file in sorted(files):
                if file.endswith(".smt2") or file.endswith(".cnf"):
                    bm = Benchmark(os.path.join(path, file), timeout)
                    if bm.group not in EXISTING_RESULTS:
                        benchmarks.append(bm)

    if len(benchmarks) == 0:
        print("Results for z3 (z3) already exist. Use --force to recreate.")
        return

    BENCHMARK_GROUPS = frozenset(bm.group for bm in benchmarks)
    
    # Written to benchmarks.p
    BENCHMARK_STATUS = {group : {"sat"     : [],
                                 "unsat"   : [],
                                 "unknown" : [],
                                 "timeout" : [],
                                 "oom"     : []}
                        for group in BENCHMARK_GROUPS}
    
    # Written to data_filename
    RESULTS = {group : {} for group in BENCHMARK_GROUPS}

    def analyze(result, progress, start_time):
        bm = result.benchmark
        group = bm.group

        result.print_summary(progress, start_time)

        # Record expected benchmark status
        bisect.insort(BENCHMARK_STATUS[group][result.prover_status], bm.sha)

        # Record verdict
        status_shorthand = {"unsat"   : "u",
                            "sat"     : "s",
                            "error"   : "e",
                            "timeout" : "t",
                            "oom"     : "o",
                            "unknown" : "?"}[result.prover_status]

        RESULTS[group][bm.sha] = {
            "status"  : status_shorthand,
            "time"    : result.cpu_time,
            "comment" : result.comment,
        }
    
    print("Perform benchmark...")
    start_time = datetime.datetime.now()
    n = 0
    if options.single:
        for bm in benchmarks:
            n += 1
            analyze(process(bm),
                    float(n * 100) / float(len(benchmarks)),
                    start_time)
    else:
        batch = 1 if options.suite in ("debug") else 5
        pool = multiprocessing.Pool()
        for result in pool.imap_unordered(process, benchmarks, batch):
            n += 1
            analyze(result,
                    float(n * 100) / float(len(benchmarks)),
                    start_time)
    
    print("Write group results...")
    for group in BENCHMARK_GROUPS:
        Path(os.path.join("results", group)).mkdir(parents=True, exist_ok=True)

        with open(os.path.join("results",
                               group,
                               "benchmarks.p"),
                  "wb") as fd:
            dump(BENCHMARK_STATUS[group], fd, -1)
        with open(os.path.join("results",
                               group,
                               data_filename),
                  "wb") as fd:
            dump(RESULTS[group], fd, -1)

    if options.report:
        create_report("z3", "z3")

if __name__ == "__main__":
    main()