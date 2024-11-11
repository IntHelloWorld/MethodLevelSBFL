import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from pprint import pprint
from typing import List

from llama_index.core.schema import NodeWithScore

sys.path.append(Path(__file__).resolve().parents[1].as_posix())
from functions.my_types import TestFailure
from projects import ALL_BUGS
from Utils.path_manager import PathManager

# def evaluate(
#     path_manager: PathManager,
#     nodes: List[NodeWithScore],
#     test_failure_obj: TestFailure
# ):
#     results = {"matches":[], "methods":[]}
#     for i, node in enumerate(nodes):
#         localized_method_text = node.text
#         results["methods"].append(localized_method_text)
#         for buggy_method in test_failure_obj.buggy_methods:
#             if buggy_method.text.replace("\r", "") == localized_method_text:
#                 results["matches"].append(i + 1)

#     with open(path_manager.res_file, 'w') as f:
#         json.dump(results, f, indent=4)


def evaluate_sf(path_manager, sbfl_res, buggy_method):
    results = {"matches":[]}
    bug_file = buggy_method["loc"]
    bug_class_name = bug_file.split("/")[-1].split(".")[0]
    bug_method_name = buggy_method["method_signature"]["method_name"]
    start_line = buggy_method["start"]
    end_line = buggy_method["end"]
    for rank, methods in enumerate(sbfl_res):
        for _, class_name, method_name, line_numbers in methods:
            for line_number in line_numbers:
                if (
                    class_name == bug_class_name
                    and method_name == bug_method_name
                    and start_line <= line_number <= end_line
                ):
                    results["matches"].append(rank + 1)
                    break

    if len(results["matches"]) == 0:
        print(f"Warning: no matched indexes found for {path_manager.project}-{path_manager.bug_id}")

    with open(path_manager.res_file, 'w') as f:
        json.dump(results, f, indent=4)


def evaluate_mf(path_manager, sbfl_res, buggy_method):
    results = {"matches":[]}
    buggy_funcs = buggy_method["functions"]
    for buggy_func in buggy_funcs:
        func_res = []
        bug_file = buggy_func["path"]
        bug_class_name = bug_file.split("/")[-1].split(".")[0]
        start_line = buggy_func["start_loc"]
        end_line = buggy_func["end_loc"]
        for rank, methods in enumerate(sbfl_res):
            for _, class_name, _, line_numbers in methods:
                for line_number in line_numbers:
                    if (
                        class_name == bug_class_name
                        and start_line <= line_number <= end_line
                    ):
                        func_res.append(rank + 1)
                        break
        results["matches"].append(func_res)

    if len(results["matches"]) == 0:
        print(f"Warning: no matched indexes found for {path_manager.project}-{path_manager.bug_id}")

    with open(path_manager.res_file, 'w') as f:
        json.dump(results, f, indent=4)


def evaluate_all_sf(res_path: str, patches_path: str=None):
    all_bugs = ALL_BUGS
    top_n = OrderedDict()
    mfr = OrderedDict()
    mar = OrderedDict()
    verbose = OrderedDict()

    version = "GrowingBugs"
    for proj in all_bugs:
        if proj not in top_n:
            top_n[proj] = OrderedDict({"top_1": 0, "top_3": 0, "top_5": 0, "top_10": 0, "total": 0})
        if proj not in verbose:
            verbose[proj] = OrderedDict()

        mfr_tmp = []
        mar_tmp = []

        for bug_id in all_bugs[proj][0]:
            if bug_id in all_bugs[proj][1]:
                continue
            res_file = os.path.join(
                res_path,
                version,
                proj,
                f"{proj}-{bug_id}",
                "result.json"
            )
            if not os.path.exists(res_file):
                print(f"Warning: result file not found for {version}-{proj}-{bug_id}")
                continue
            with open(res_file, 'r') as f:
                results = json.load(f)
                matched_indexes = results["matches"]
            top_n[proj]["total"] += 1
            verbose[proj][bug_id] = results
            if matched_indexes:
                if matched_indexes[0] == 1:
                    top_n[proj]["top_1"] += 1
                if matched_indexes[0] <= 3:
                    top_n[proj]["top_3"] += 1
                if matched_indexes[0] <= 5:
                    top_n[proj]["top_5"] += 1
                if matched_indexes[0] <= 10:
                    top_n[proj]["top_10"] += 1
                mfr_tmp.append(matched_indexes[0])
                mar_tmp.append(sum(matched_indexes) / len(matched_indexes))
            else:
                print(f"Warning: no matched indexes found for {version}-{proj}-{bug_id}")

            if patches_path:
                patch_file = os.path.join(patches_path, f"{proj}-{bug_id}-validated.jsonl")
                if os.path.exists(patch_file):
                    with open(patch_file, 'r') as f:
                        patches = json.load(f)
                    for patch in patches:
                        if patch["patch_status"] == "PLAUSIBLE":
                            verbose[proj][bug_id]["status"] = "SUCCESS"
                            break
                    else:
                        verbose[proj][bug_id]["status"] = "FAILURE"
                else:
                    print(f"Warning: patch file not found for {version}-{proj}-{bug_id}")
                    verbose[proj][bug_id]["status"] = "NONE"

        if mfr_tmp:
            mfr[proj] = sum(mfr_tmp) / len(mfr_tmp)
        else:
            mfr[proj] = None

        if mar_tmp:
            mar[proj] = sum(mar_tmp) / len(mar_tmp)
        else:
            mar[proj] = None

    all_zero_projecs = []
    for proj in top_n:
        all_zero = True
        for k in top_n[proj]:
            if top_n[proj][k] != 0:
                all_zero = False
                break
        if all_zero:
            all_zero_projecs.append(proj)

    for proj in all_zero_projecs:
        del top_n[proj]
        del mfr[proj]
        del mar[proj]

    # print("Top N:")
    # pprint(top_n)
    # print("MFR:")
    # pprint(mfr)
    # print("MAR:")
    # pprint(mar)
    with open(os.path.join(res_path, version, "all_topN_result.json"), 'w') as f:
        json.dump(top_n, f, indent=2)
    with open(os.path.join(res_path, version, "all_MFR_result.json"), 'w') as f:
        json.dump(mfr, f, indent=2)
    with open(os.path.join(res_path, version, "all_MAR_result.json"), 'w') as f:
        json.dump(mar, f, indent=2)
    with open(os.path.join(res_path, version, "verbose_result.json"), "w") as f:
        json.dump(verbose, f, indent=2)

    n_all_bugs = sum([top_n[proj]["total"] for proj in top_n])
    n_all_top_1 = sum([top_n[proj]["top_1"] for proj in top_n])
    n_all_top_3 = sum([top_n[proj]["top_3"] for proj in top_n])
    n_all_top_5 = sum([top_n[proj]["top_5"] for proj in top_n])
    n_all_top_10 = sum([top_n[proj]["top_10"] for proj in top_n])
    print(f"Total bugs: {n_all_bugs}")
    print(f"ALL Top 1: {n_all_top_1}")
    print(f"ALL Top 3: {n_all_top_3}")
    print(f"ALL Top 5: {n_all_top_5}")
    print(f"ALL Top 10: {n_all_top_10}")


def evaluate_all_mf(res_path: str):
    all_bugs = ALL_BUGS
    top_n = OrderedDict()
    verbose = OrderedDict()
    
    version = "GrowingBugs"
    for proj in all_bugs:
        if proj not in top_n:
            top_n[proj] = OrderedDict({"top_1": 0, "top_3": 0, "top_5": 0, "top_10": 0, "total": 0})
        if proj not in verbose:
            verbose[proj] = OrderedDict()

        
        for bug_id in all_bugs[proj][0]:
            if bug_id in all_bugs[proj][1]:
                continue
            res_file = os.path.join(
                res_path,
                version,
                proj,
                f"{proj}-{bug_id}",
                "result.json"
            )
            if not os.path.exists(res_file):
                print(f"Warning: result file not found for {version}-{proj}-{bug_id}")
                continue
            with open(res_file, 'r') as f:
                results = json.load(f)
                matched_indexes = results["matches"]
                top_n[proj]["total"] += 1
            
            verbose[proj][bug_id] = matched_indexes
            
            first_ranks = [m[0] for m in matched_indexes if m]
            first_rank = first_ranks[0] if first_ranks else None
            if first_rank:
                if first_rank == 1:
                    top_n[proj]["top_1"] += 1
                if first_rank <= 3:
                    top_n[proj]["top_3"] += 1
                if first_rank <= 5:
                    top_n[proj]["top_5"] += 1
                if first_rank <= 10:
                    top_n[proj]["top_10"] += 1
            else:
                print(f"Warning: no matched indexes found for {version}-{proj}-{bug_id}")
    
    all_zero_projecs = []
    for proj in top_n:
        all_zero = True
        for k in top_n[proj]:
            if top_n[proj][k] != 0:
                all_zero = False
                break
        if all_zero:
            all_zero_projecs.append(proj)
    
    for proj in all_zero_projecs:
        del top_n[proj]
    
    with open(os.path.join(res_path, version, "all_topN_result.json"), 'w') as f:
        json.dump(top_n, f, indent=2)
    with open(os.path.join(res_path, version, "verbose_result.json"), 'w') as f:
        json.dump(verbose, f, indent=2)
    
    n_all_bugs = sum([top_n[proj]["total"] for proj in top_n])
    n_all_top_1 = sum([top_n[proj]["top_1"] for proj in top_n])
    n_all_top_3 = sum([top_n[proj]["top_3"] for proj in top_n])
    n_all_top_5 = sum([top_n[proj]["top_5"] for proj in top_n])
    n_all_top_10 = sum([top_n[proj]["top_10"] for proj in top_n])
    print(f"Total bugs: {n_all_bugs}")
    print(f"ALL Top 1: {n_all_top_1}")
    print(f"ALL Top 3: {n_all_top_3}")
    print(f"ALL Top 5: {n_all_top_5}")
    print(f"ALL Top 10: {n_all_top_10}")


def analyze_verbose_result(verbose_result_path: str, tolerance: int=10):
    verbose_analysis = {"should_be_success": [], "should_be_failure": [], "is_success": [], "is_failure": [], "no_patch": []}
    with open(verbose_result_path, 'r') as f:
        verbose_result = json.load(f)
    for proj in verbose_result:
        for bug_id in verbose_result[proj]:
            first_rank = verbose_result[proj][bug_id]["matches"][0]
            status = verbose_result[proj][bug_id]["status"]
            if status == "NONE":
                verbose_analysis["no_patch"].append(f"{proj}-{bug_id}")
                continue
            
            if first_rank <= tolerance and status == "SUCCESS":
                verbose_analysis["is_success"].append(f"{proj}-{bug_id}")
            elif first_rank > tolerance and status == "FAILURE":
                verbose_analysis["is_failure"].append(f"{proj}-{bug_id}")
            elif first_rank <= tolerance and status == "FAILURE":
                verbose_analysis["should_be_success"].append(f"{proj}-{bug_id}")
            elif first_rank > tolerance and status == "SUCCESS":
                verbose_analysis["should_be_failure"].append(f"{proj}-{bug_id}")

    with open(os.path.join(res_path, "GrowingBugs", "verbose_analysis.json"), "w") as f:
        json.dump(verbose_analysis, f, indent=2)


if __name__ == "__main__":
    res_path = "/root/APR/FLtools/MethodLevelSBFL/DebugResult/sf-evaluation"
    patches_path = "/root/APR/APRtools/SRepair/result/GrowingBug-sf/"
    evaluate_all_sf(res_path, patches_path)
    analyze_verbose_result(os.path.join(res_path, "GrowingBugs", "verbose_result.json"))
    
    # res_path = "/root/APR/FLtools/MethodLevelSBFL/DebugResult/mf-evaluation"
    # evaluate_all_mf(res_path)
