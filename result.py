import datetime

class Result(object):
    def __init__(self, bm, status, comment, cpu_time):
        assert status in ("sat", "unsat", "unknown", "timeout", "oom", "error")
        self.benchmark     = bm
        self.prover_status = status
        self.comment       = comment
        self.cpu_time      = cpu_time

        if (self.prover_status in ("sat", "unsat") and
            self.benchmark.expected in ("sat", "unsat") and
            self.prover_status != self.benchmark.expected):
            self.status = "unsound"
            self.comment = f"result {self.prover_status} is not {self.benchmark.expected}"
        else:
            self.status = self.prover_status

    def __str__(self):
        map = {
            "sat"     : 's ✓',
            "unsat"   : 'u ✓',
            "unknown" : ' ? ',
            "timeout" : ' ⌛ ',
            "oom"     : 'oom',
            "error"   : 'err',
            "unsound" : ' ! ',
        }

        return f"(runtime:{self.cpu_time}) [{map[self.status]}] {self.benchmark.name}"

    def print_summary(self, progress, start_time):
        now = datetime.datetime.now()
        elapsed = now - start_time
        elapsed_s = float(elapsed.microseconds) / 1000000.0 + float(elapsed.seconds)
        per_percent = elapsed_s / progress
        remaining = per_percent * (100.0 - progress)

        print(f"<{progress:.1f}%> Time Remaining:{remaining:.0f} {str(self)}")
        if self.status in ("error", "unsound"):
            print(self.comment.strip())