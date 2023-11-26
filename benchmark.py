import os
import subprocess
import time
import re
from result import Result
    
class Benchmark:
    def __init__(self, fn, timeout, solver_bin, solver_args):
        self.path      = fn # anni_2022/{hash}-{name}.cnf
        basename = os.path.basename(fn)
        pos = basename.find("-")
        self.hash       = basename[:pos]
        self.name      = basename[pos+1:]
        self.group     = fn.split("/")[0] # anni_2022
        self.solver_bin = solver_bin
        self.solver_args = solver_args
        self.limit_time = timeout
        self.limit_memory = 2000

    def execute(self):
        start_time = time.perf_counter()
        log = subprocess.run(f"{self.solver_bin} {self.solver_args} -T:{self.limit_time} -memory:{self.limit_memory} {self.path}",
                             capture_output=True, shell=True, text=True)
        end_time = time.perf_counter()

        elapsed_s = end_time - start_time
        stdout_lines = log.stdout.splitlines()
        status = None
        status_line = stdout_lines[0]
        if re.search("sat|SATISFIABLE", status_line):
            status = "sat"
        elif re.search("unsat|UNSATISFIABLE", status_line):
            status = "unsat"
        elif re.search("timeout", status_line):
            status = "timeout"
        elif re.search("oom", status_line):
            status = "oom"
        elif re.search("error", status_line):
            status = "error"
        else:
            assert False

        return Result(self, status, log.stderr, elapsed_s)