import argparse
import json
import os
import pickle
import shutil
import sys

from Evaluation.evaluate import evaluate
from functions.d4j import check_out, get_failed_tests, get_properties
from functions.sbfl import parse_sbfl, parse_sbfl_version_2
from preprocess.read_nodes import get_methods_for_sbfl
from Utils.path_manager import PathManager

root = os.path.dirname(__file__)
sys.path.append(root)

def main():
    parser = argparse.ArgumentParser(description='argparse')
    parser.add_argument('--config', type=str, default="default",
                        help="Name of config, which is used to load configuration under Config/")
    parser.add_argument('--version', type=str, default="GrowingBugs",
                        help="Version of defects4j")
    parser.add_argument('--project', type=str, default="AaltoXml",
                        help="Name of project, your debug result will be generated in DebugResult/d4jversion_project_bugID")
    parser.add_argument('--bugID', type=int, default=1,
                        help="Prompt of software")
    parser.add_argument('--subproj', type=str, required=False, default="",
                        help="The subproject of the project")
    parser.add_argument('-c', '--clear', type=bool, default=True,
                        help="If clear the checkout project")
    args = parser.parse_args()

    # ----------------------------------------
    #          Init Test Failure
    # ----------------------------------------

    path_manager = PathManager(args)
    path_manager.logger.info("*" * 100)
    path_manager.logger.info(f"Start debugging bug {args.version}-{args.project}-{args.bugID}")
    bug_name = f"{args.project}-{args.bugID}"
    
    if os.path.exists(path_manager.res_file):
        path_manager.logger.info(f"d4j{args.version}-{args.project}-{args.bugID} already finished, skip!")
        return

    # check out the d4j project
    # path_manager.logger.info("[checkout] start...")
    # check_out(path_manager)
    
    # get cahed buggy method information
    path_manager.logger.info("[get buggy method infos] start...")
    with open(path_manager.buggy_methods_file, "r") as f:
        buggy_methods = json.load(f)
    if bug_name not in buggy_methods:
        path_manager.logger.error(f"Bug {bug_name} not found in the buggy methods cached file")
        return
    
    # get bug specific information
    # path_manager.logger.info("[get bug properties] start...")
    # get_properties(path_manager)
    
    # ----------------------------------------
    #          SBFL results
    # ----------------------------------------

    sbfl_res = None
    sbfl_res = parse_sbfl_version_2(path_manager.sbfl_file)
    if len(sbfl_res) == 0:
        path_manager.logger.error(f"Empty SBFL results in {path_manager.sbfl_file}")
        return

    # ----------------------------------------
    #          Load Index
    # ----------------------------------------

    # path_manager.logger.info("[load data] start...")
    # nodes = get_methods_for_sbfl(path_manager, sbfl_res)
    
    # with open(path_manager.retrieved_nodes_file, "wb") as f:
    #     pickle.dump(nodes, f)
    
    # ----------------------------------------
    #          Evaluate
    # ----------------------------------------
    
    evaluate(path_manager, sbfl_res, buggy_methods)
    
    if args.clear:
        shutil.rmtree(path_manager.buggy_path, ignore_errors=True)
        shutil.rmtree(path_manager.fixed_path, ignore_errors=True)

if __name__ == "__main__":
    main()
