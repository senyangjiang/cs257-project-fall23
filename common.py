import pickle
from copy import deepcopy
import os
import hashlib
import pickle

SCORES = ("solved", "unknown", "timeout", "oom", "error", "unsound")

to_long_score = {"s" : "solved",
                 "?" : "unknown",
                 "t" : "timeout",
                 "o" : "oom",
                 "e" : "error",
                 "u" : "unsound"}

BLANK_SOLVER_DATA = {
    "group_results" : {},
    "group_summary" : {},
    "total_summary" : {
        "score"        : {score: 0 for score in SCORES},
        "average"      : {score: 0.0 for score in SCORES}
    },
    "prover_kind"   : None,
    "prover_bin"    : None,
}

def secure_name(bm_name):
    m = hashlib.sha1()
    m.update(os.path.normpath(bm_name).encode())
    return m.hexdigest()

def load_benchmark_status():
    print("Loading benchmark summaries")
    # returns a dictionay with benchmark status
    # bm_name -> {"status" : s (sat) | u (unsat) | ? (unknown)
    #             "name"   : original name}
    data = {}

    if not os.path.isdir("results"):
        return data

    # Benchmarks are stored with a hashed name, this allows us to
    # pretty-print the ones that are in the testsuite here.
    reverse_map = {}
    for path, _, files in os.walk("."):
        for file in files:
            if file.endswith(".smt2") or file.endswith(".cnf"):
                sha = secure_name(os.path.join(path, file))
                reverse_map[sha] = os.path.normpath(os.path.join(path, file))

    for group in os.listdir("results"):
        if not os.path.isdir(os.path.join("results", group)):
            continue
        with open(os.path.join("results", group, "benchmarks.p"), "rb") as fd:
            result = pickle.load(fd)
        assert set(result) == set(["sat", "unsat", "unknown", "timeout", "oom"])
        for status in result:
            for bm in result[status]:
                data[bm] = {"status" : {"sat"     : "s",
                                        "unsat"   : "u",
                                        "unknown" : "?",
                                        "timeout" : "t",
                                        "oom"     : "o",}[status],
                            "name"   : reverse_map.get(bm, "sha<%s>" % bm)}

    return data

def load_results(solver_kind, solver_bin, benchmark_status=None):
    print(f"Loading results for {solver_kind} ({solver_bin})")
    data_filename = f"data_{solver_kind}_{solver_bin}.p"

    data = deepcopy(BLANK_SOLVER_DATA)
    data["prover_kind"] = solver_kind
    data["prover_bin"]  = solver_bin

    if not os.path.isdir("results"):
        return data

    if benchmark_status is None:
        benchmark_status = load_benchmark_status()

    group_total = 0 # How many groups we have participated in

    for group in os.listdir("results"):
        if not os.path.isfile(os.path.join("results", group, data_filename)):
            continue
        with open(os.path.join("results", group, data_filename), "rb") as fd:
            data["group_results"][group] = pickle.load(fd)

        collect_group_result(data, group, benchmark_status)
        group_total += 1

    # Add aggregated total summary
    collect_final_result(data, group_total)

    print("########FINAL DATA##########")
    print(data)
    return data

def collect_group_result(data, group, benchmark_status):
    data["group_summary"][group] = {
        "score"        : {score: 0 for score in SCORES},
        "average"      : {score: 0.0 for score in SCORES},
        "time"         : 0.0,
    }
    summary = data["group_summary"][group]

    totals = data["total_summary"]

    for bm, result in data["group_results"][group].items():
        assert bm in benchmark_status

        # Set score (solved, unsound, etc.)
        if result["status"] in ("s", "u"):
            if benchmark_status[bm]["status"] in ("s", "u"):
                if result["status"] == benchmark_status[bm]["status"]:
                    result["score"] = "s" # solved
                else:
                    result["score"] = "u" # unsound
            else:
                assert benchmark_status[bm]["status"] == "?"
                result["score"] = "s" # solved
        else:
            assert result["status"] in ("e", # error
                                        "t", # timeout
                                        "o", # out-of-memory
                                        "?") # unknown
            result["score"] = result["status"]

        # Contribute to group and overall totals
        summary["score"][to_long_score[result["score"]]] += 1
        totals["score"][to_long_score[result["score"]]] += 1
        summary["time"] += result["time"]

    # Add aggregated group summary
    bm_total = sum(summary["score"].values())
    for score in SCORES:
        summary["average"][score] = (
            float(summary["score"][score] * 100) /
            float(bm_total)
        )

def collect_final_result(data, group_total):
    totals = data["total_summary"]
    for score in SCORES:
        if group_total > 0:
            totals["average"][score] = (
                sum(data["group_summary"][group]["average"][score]
                    for group in data["group_summary"]) /
                float(group_total))
        else:
            totals["average"][score] = 0.0
    totals["time"] = sum(data["group_summary"][group]["time"] 
                         for group in data["group_summary"])