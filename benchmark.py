import os
import subprocess
import time
import re
from result import Result
    
class Benchmark:
    def __init__(self, fn, timeout, solver_kind, solver_args):
        self.path      = fn # anni_2022/{hash}-{name}.cnf
        basename = os.path.basename(fn)
        pos = basename.find("-")
        self.hash       = basename[:pos]
        self.name      = basename[pos+1:]
        self.group     = fn.split("/")[0] # anni_2022
        self.solver_kind = solver_kind
        self.solver_args = solver_args
        self.limit_time = timeout
        self.limit_memory = 2000

    def execute(self):
        COMMAND_MAP = {
            "z3": f"solver/z3 {self.solver_args} -T:{self.limit_time} -memory:{self.limit_memory} {self.path}",
            "kissat": f"solver/kissat-3.1.0 {self.solver_args} -q -n --time={self.limit_time} {self.path}",
            "cadical": f"solver/cadical-1.9.0 {self.solver_args} -q -n -t {self.limit_time} {self.path}",
            "cryptominisat": f"solver/cryptominisat5 {self.solver_args} --verb=0 --maxtime={self.limit_time} {self.path}"
        }
        print(COMMAND_MAP[self.solver_kind])
        start_time = time.perf_counter()
        log = subprocess.run(COMMAND_MAP[self.solver_kind],
                             capture_output=True, shell=True, text=True)
        end_time = time.perf_counter()

        elapsed_s = end_time - start_time
        print("stdout:")
        print(log.stdout)
        print("stderr:")
        print(log.stderr)
        stdout_lines = log.stdout.splitlines()
        status = None
        if stdout_lines:
            status_line = stdout_lines[0]
            if re.search("unsat|UNSATISFIABLE", status_line):
                status = "unsat"
            elif re.search("sat|SATISFIABLE", status_line):
                status = "sat"
            elif re.search("timeout|UNKNOWN|INDETERMINATE", status_line):
                status = "unknown"
            elif re.search("oom", status_line):
                status = "oom"
            elif re.search("error", status_line):
                status = "error"
            else:
                assert False
        else:
            status = "unknown"

        return Result(self, status, log.stderr, elapsed_s)