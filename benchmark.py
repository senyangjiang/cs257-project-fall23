import os
import subprocess
import time
import re
from common import secure_name
from result import Result

def process_smt_file(fn, strip_logic):
    status = "unknown"
    logic  = None
    data   = ""

    with open(fn, "rU") as fd:
        for raw_line in fd:
            line = ""
            in_token = False
            in_comment = False
            for c in raw_line:
                if in_token and c == "|":
                    in_token = False
                elif c == "|":
                    in_token = True
                elif in_token and c == ";":
                    pass
                elif c == ";":
                    in_comment = True
                    break
                elif c == "\n":
                    break
                line += c

            if "set-info" in line and ":status" in line:
                tokens = line.strip().split()
                assert tokens[0] == "(set-info"
                assert tokens[1] == ":status"
                status = tokens[2].strip(")")
                assert status in ("unknown", "sat", "unsat")
            elif "(set-logic" in line:
                tokens = line.strip().split()
                assert tokens[0] == "(set-logic"
                assert tokens[1].endswith(")")
                logic = tokens[1].strip(")")
                if not strip_logic and logic is not None:
                    data += "(set-logic %s)\n" % logic
            else:
                data += line + "\n"

        return status, logic, data
    
class Benchmark:
    def __init__(self, fn, timeout_override=None):
        self.path      = fn # ABV/test/bench.smt2
        self.sha       = secure_name(fn)
        self.name      = os.path.basename(fn) # bench.smt2
        self.group     = fn.split("/")[0] # ABV
        self.logic     = None
        self.expected  = "unknown"
        self.data      = None

        if timeout_override is None:
            self.limit_time = 1
        else:
            self.limit_time = timeout_override

        self.limit_memory = 2000

    def load(self, keep_logic):
        self.expected, self.logic, self.data = process_smt_file(self.path,
                                                                not keep_logic)

    def unload(self):
        self.data = None

    def execute(self):
        start_time = time.perf_counter()
        log = subprocess.run(f"z3 -st -T:{self.limit_time} -memory:{self.limit_memory} {self.path}",
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

        # stderr_lines = log.stderr.splitlines()
        # print(log.stdout)
        # print(log.stderr)
        # elapsed_s = float(re.search("\d+\.\d+", stderr_lines[-1]))
        return Result(self, status, log.stderr, elapsed_s)