import argparse
import json
import os
import subprocess
import sys
from argparse import Namespace

from Evaluation.evaluate import evaluate_mf, evaluate_sf
from functions.generate_dataset import make_fix_dataset, sample_fix_dataset
from functions.sbfl import parse_sbfl_version_2
from projects import SBF
from SBFL.runMultiprocess_GrowingBugs_partial import projDict
from Utils.path_manager import PathManager

root = os.path.dirname(__file__)
sys.path.append(root)

# ALL_BUGS = SBF
ALL_BUGS = projDict

def run_all_bugs(config_name: str, top_k: int, clear: bool = True):
    version = "GrowingBugs"
    for proj in ALL_BUGS:
        bugIDs = ALL_BUGS[proj][0]
        deprecatedIDs = ALL_BUGS[proj][1]
        subproj = ALL_BUGS[proj][2]
        if subproj == 'None':
            subproj = ""
        for bug_id in bugIDs:
            
            bug_name = f"{proj}-{bug_id}"
            
            if bug_id in deprecatedIDs:
                continue
            
            run_one_bug(config_name, version, proj, bug_id, clear, subproj)
    
    sample_fix_dataset(ALL_BUGS, top_k)

def run_one_bug(config_name, version, proj, bug_id, clear, subproj):
    args = Namespace(
        config=config_name,
        version=version,
        project=proj,
        bugID=bug_id,
        subproj=subproj,
        clear=clear
    )

    path_manager = PathManager(args)
    path_manager.logger.info("*" * 100)
    path_manager.logger.info(f"Start debugging bug {args.version}-{args.project}-{args.bugID}")

    if os.path.exists(path_manager.dataset_file):
        path_manager.logger.info(f"d4j{args.version}-{args.project}-{args.bugID} already finished, skip!")
        return

    # ----------------------------------------
    #          SBFL results
    # ----------------------------------------

    sbfl_res = None
    sbfl_res = parse_sbfl_version_2(path_manager.sbfl_file)
    if len(sbfl_res) == 0:
        path_manager.logger.error(f"Empty SBFL results in {path_manager.sbfl_file}")
        return

    # ----------------------------------------
    #          make dataset for fix tool
    # ----------------------------------------

    make_fix_dataset(path_manager, sbfl_res)

    # ----------------------------------------
    #          Evaluate
    # ----------------------------------------

    # if config_name == "sf-evaluation":
    #     evaluate_sf(path_manager, sbfl_res, buggy_method)
    # elif config_name == "mf-evaluation":
    #     evaluate_mf(path_manager, sbfl_res, buggy_method)
    # else:
    #     raise ValueError(f"Unknown config name: {config_name}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", type=int, required=False, default=1)
    args = parser.parse_args()

    config_name = "sf-evaluation"
    run_all_bugs(config_name, args.k, True)

    # config_name = "mf-evaluation"
    # mf_file = "/root/APR/FLtools/MethodLevelSBFL/Evaluation/GrowingBug-mf.json"
    # run_all_bugs(config_name, mf_file, True)
