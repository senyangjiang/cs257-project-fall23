import datetime

class Result(object):
    def __init__(self, bm, status, comment, cpu_time):
        assert status in ("sat", "unsat", "unknown", "timeout", "oom", "error")
        self.benchmark     = bm
        self.status        = status
        self.comment       = comment
        self.cpu_time      = cpu_time

    def __str__(self):
        MAP = {
            "sat"     : 's ✓',
            "unsat"   : 'u ✓',
            "unknown" : ' ? ',
            "timeout" : ' ⌛ ',
            "oom"     : 'oom',
            "error"   : 'err',
        }

        return f"(runtime:{self.cpu_time}) [{MAP[self.status]}] {self.benchmark.name}"

    def print_summary(self, progress, start_time):
        now = datetime.datetime.now()
        elapsed = now - start_time
        elapsed_s = float(elapsed.microseconds) / 1000000.0 + float(elapsed.seconds)
        per_percent = elapsed_s / progress
        remaining = per_percent * (100.0 - progress)

        print(f"<{progress:.1f}%> Time Remaining:{remaining:.0f} {str(self)}")
        if self.status in ("error"):
            print(self.comment.strip())

    def add_csv(self, df):
        # status | time
        df.loc[len(df.index)] = [self.status, self.cpu_time]