import time
import signal
from multiprocessing import Process, Queue

import os
from sat_instance.sat_instance import SATInstance
import glob
import csv

Q = Queue()

def handle_timeout(signum, frame):
    raise TimeoutError

def feature_gen(file_name):
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(60)  # 20 seconds
    try:
        sat_inst = SATInstance(file_name, preprocess=True)
        if sat_inst.solved:
            return

        t1 = time.time()
        sat_inst.gen_basic_features()
        t2 = time.time()
        sat_inst.gen_dpll_probing_features()
        # linux only
        sat_inst.gen_local_search_probing_features()
        t3 = time.time()
        # sat_inst.gen_ansotegui_features()
        # t4 = time.time()
        # sat_inst.gen_manthey_alfonso_graph_features()
        # t5 = time.time()

        basename = os.path.basename(file_name)
        pos = basename.find("-")
        sat_inst.features_dict["file_name"] = os.path.basename(basename[:pos])
        sat_inst.features_dict["satzilla_base_t"] = (t2 - t1)
        sat_inst.features_dict["satzilla_probe_t"] = (t3 - t2)
        # sat_inst.features_dict["ansotegui_t"] = (t4 - t3)
        # sat_inst.features_dict["alfonso_t"] = (t5 - t4)
        Q.put(sat_inst.features_dict)
    except TimeoutError:
        print(f"TIMEOUT: Skipped {file_name}")
    finally:
        signal.alarm(0)

def bulk_gen_features(path_to_cnfs="/projects/satdb/dataset_final/", results_csv="features.csv", file_type="*"):
    # for each file, we need to create a sat_instance for it
    # file_list = glob.glob(path_to_cnfs + "sat_4*.cnf")
    file_list = glob.glob(path_to_cnfs + file_type + ".cnf")
    dict_keys = ['c', 'v', 'clauses_vars_ratio', 'vars_clauses_ratio', 'vcg_var_mean', 'vcg_var_coeff', 'vcg_var_min',
     'vcg_var_max', 'vcg_var_entropy', 'vcg_clause_mean', 'vcg_clause_coeff', 'vcg_clause_min', 'vcg_clause_max',
     'vcg_clause_entropy', 'vg_mean', 'vg_coeff', 'vg_min', 'vg_max', 'pnc_ratio_mean', 'pnc_ratio_coeff',
     'pnc_ratio_min', 'pnc_ratio_max', 'pnc_ratio_entropy', 'pnv_ratio_mean', 'pnv_ratio_coeff', 'pnv_ratio_min',
     'pnv_ratio_max', 'pnv_ratio_entropy', 'pnv_ratio_stdev', 'binary_ratio', 'ternary_ratio', 'ternary+',
     'hc_fraction', 'hc_var_mean', 'hc_var_coeff', 'hc_var_min', 'hc_var_max', 'hc_var_entropy',
     'unit_props_at_depth_1', 'unit_props_at_depth_4', 'unit_props_at_depth_16', 'unit_props_at_depth_64',
     'unit_props_at_depth_256', 'mean_depth_to_contradiction_over_vars', 'estimate_log_number_nodes_over_vars',
     'saps_BestSolution_Mean', 'saps_BestSolution_CoeffVariance', 'saps_FirstLocalMinStep_Mean',
     'saps_FirstLocalMinStep_CoeffVariance', 'saps_FirstLocalMinStep_Median', 'saps_FirstLocalMinStep_Q.10',
     'saps_FirstLocalMinStep_Q.90', 'saps_BestAvgImprovement_Mean', 'saps_BestAvgImprovement_CoeffVariance',
     'saps_FirstLocalMinRatio_Mean', 'saps_FirstLocalMinRatio_CoeffVariance', 'saps_EstACL_Mean',
     'gsat_BestSolution_Mean', 'gsat_BestSolution_CoeffVariance', 'gsat_FirstLocalMinStep_Mean',
     'gsat_FirstLocalMinStep_CoeffVariance', 'gsat_FirstLocalMinStep_Median', 'gsat_FirstLocalMinStep_Q.10',
     'gsat_FirstLocalMinStep_Q.90', 'gsat_BestAvgImprovement_Mean', 'gsat_BestAvgImprovement_CoeffVariance',
     'gsat_FirstLocalMinRatio_Mean', 'gsat_FirstLocalMinRatio_CoeffVariance', 'gsat_EstACL_Mean',
     "file_name", "satzilla_base_t", "satzilla_probe_t"]

    with open(results_csv, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=dict_keys)
        writer.writeheader()

        for i, file_name in enumerate(sorted(file_list)[:500]):
            print(file_name)
            print("file ", i, " out of ", len(file_list))
            
            process = Process(target=feature_gen, args=(file_name,))
            process.start()
            process.join()
            if not Q.empty():
                writer.writerow(Q.get())
            f.flush()
            


if __name__ == "__main__":
    # path_to_cnfs = "cnf_examples/"
    # classes = ["clique_", "colour_", "cliquecoloring", "dominating", "matching", "op", "php", "subsetcard", "tiling", "tseitin"]
    # binary = ["sat", "unsat"]
    path_to_cnfs = "/home/ubuntu/cs257-project-fall23/anni_2022/"
    results_csv = "features_dpll_preprocess_500.csv"

    bulk_gen_features(path_to_cnfs=path_to_cnfs, results_csv=results_csv)
