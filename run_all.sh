#! /bin/bash

set -x

python3 run.py --count=300 --solver_kind=z3
python3 run.py --count=300 --solver_kind=z3 --solver_args="sat.local_search=true" --add_to_csv="output.csv"
python3 run.py --count=300 --solver_kind=z3 --solver_args="sat.lookahead_simplify=true" --add_to_csv="output.csv"
python3 run.py --count=300 --solver_kind=z3 --solver_args="sat.ddfw_search=true" --add_to_csv="output.csv"
# python3 run.py --count=300 --solver_kind=kissat --add_to_csv="output.csv"
# python3 run.py --count=300 --solver_kind=cadical --add_to_csv="output.csv"
# python3 run.py --count=300 --solver_kind=cryptominisat --add_to_csv="output.csv"