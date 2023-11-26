import argparse
import multiprocessing
import os
import datetime
import pandas as pd

from common import *
from benchmark import Benchmark

def process(bm):
    return bm.execute()
    
def main():
    ap = argparse.ArgumentParser()
    ### Solver ###
    ap.add_argument("--solver_kind",
                    default="z3",
                    choices=["z3"])
    ap.add_argument("--solver_args",
                    default="")
    ap.add_argument("--solver_bin",
                    default="z3",
                    choices=["z3"])
    ### Benchmark ###
    ap.add_argument("--suite",
                    default="anni_2022",
                    choices=["anni_2022"])
    ap.add_argument("--count",
                    type=int,
                    default=None)
    ### Execution ###
    ap.add_argument("--parallel",
                    default=False,
                    action="store_true")
    ap.add_argument("--timeout",
                    default=1,
                    type=int,
                    help="set global timeout, default is 60 seconds")
    ### Result ###
    ap.add_argument("--input_csv",
                    default=None)
    ap.add_argument("--report",
                    default=False,
                    action="store_true")
    options = ap.parse_args()

    bench_dirs = []
    if options.suite == "anni_2022":
        bench_dirs.append("anni_2022")

    print("Assembling benchmarks...")
    benchmarks = []
    for d in bench_dirs:
        cnt = 0
        for path, _, files in os.walk(d):
            for file in sorted(files):
                if file.endswith(".cnf"):
                    bm = Benchmark(os.path.join(path, file), 
                                   options.timeout, 
                                   options.solver_bin, 
                                   options.solver_args)
                    benchmarks.append(bm)
                    cnt += 1
                    if options.count and cnt >= options.count:
                        break
        print(f"Loaded {cnt} benchmarks from {d}")

    print("Read any previous benchmark results...")
    base = None
    if options.input_csv and os.path.exists(options.input_csv):
        base = pd.read_csv(options.input_csv)
    else:
        base = pd.DataFrame(columns=["hash", "benchmark"])
        for bm in benchmarks:
            base.loc[len(base.index)] = [bm.hash, bm.name]

    print(base)

    print("Perform benchmark...")
    solver_id = f"{options.solver_kind}+'{options.solver_args}'"
    df = pd.DataFrame(columns=[f"time({solver_id})", f"result({solver_id})"])

    start_time = datetime.datetime.now()
    n = 0
    
    if options.parallel:
        batch = 5
        pool = multiprocessing.Pool()
        for result in pool.map(process, benchmarks, batch):
            n += 1
            result.print_summary(float(n * 100) / float(len(benchmarks)), start_time)
            result.add_csv(df)
    else:
        for bm in benchmarks:
            n += 1
            result = process(bm)
            result.print_summary(float(n * 100) / float(len(benchmarks)), start_time)
            result.add_csv(df)

    print(df)
    print("Collect Results...")
    out = pd.concat([base, df], axis=1)
    print(out)
    out.to_csv('output.csv', index=True)

if __name__ == "__main__":
    main()