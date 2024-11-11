import json
import os
import shutil
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
from functions.d4j import check_out, get_properties
from functions.MethodExtractor.java_method_extractor import JavaMethodExtractor
from projects import SBF
from Utils.path_manager import PathManager

ALL_BUGS = SBF


def make_fix_dataset(path_manager: PathManager, sbfl_res, buggy_method):

    suspicious_methods = []
    java_method_extractor = JavaMethodExtractor()

    # check out the d4j project
    path_manager.logger.info("[checkout] start...")
    check_out(path_manager)

    # get bug specific information
    path_manager.logger.info("[get bug properties] start...")
    get_properties(path_manager)

    trigger_test = buggy_method["trigger_test"]

    methods_cache = {}
    for rank in sbfl_res[:50]:
        for pkg_name, class_name, method_name, line_numbers in rank:
            java_file = os.path.join(
                path_manager.buggy_path,
                path_manager.src_prefix,
                pkg_name.replace(".", "/"),
                class_name + ".java",
            )
            if not os.path.exists(java_file):
                is_found = False
                # dispatch outer class name
                while class_name.rfind("$") != -1:
                    class_name = class_name[:class_name.rfind("$")]
                    java_file = os.path.join(
                        path_manager.buggy_path,
                        path_manager.src_prefix,
                        pkg_name.replace(".", "/"),
                        class_name + ".java",
                    )
                    if os.path.exists(java_file):
                        is_found = True
                        break
                if not is_found:
                    print(f"Warning: File {java_file} not found")
                    continue

            key = f"{pkg_name}${class_name}"
            if key in methods_cache:
                methods = methods_cache[key]
            else:
                with open(java_file, "r") as f:
                    java_code = f.read()
                methods = java_method_extractor.get_java_methods(java_code)
                methods_cache[key] = methods

            for method in methods:
                if (
                    method.name == method_name
                    and any(method.loc[0][0] + 1 <= ln <= method.loc[1][0] + 1 for ln in line_numbers)
                ):  
                    suspicious_method = {
                        "buggy": method.code,
                        "fix": "",
                        "start": method.loc[0][0] + 1,
                        "end": method.loc[1][0] + 1,
                        "loc": os.path.join(path_manager.subproj, pkg_name.replace(".", "/"), class_name + ".java"),
                        "method_signature": "",
                        "trigger_test": trigger_test,
                        "buggy_code_comment": method.comment,
                    }
                    suspicious_methods.append(suspicious_method)

    with open(path_manager.dataset_file, "w") as f:
        json.dump(suspicious_methods, f, indent=2)

    shutil.rmtree(path_manager.buggy_path, ignore_errors=True)
    shutil.rmtree(path_manager.fixed_path, ignore_errors=True)


def sample_fix_dataset():
    version = "GrowingBugs"
    dataset = {}
    for proj in ALL_BUGS:
        bugIDs = ALL_BUGS[proj][0]
        deprecatedIDs = ALL_BUGS[proj][1]
        subproj = ALL_BUGS[proj][2]
        if subproj == "None":
            subproj = ""
        for bug_id in bugIDs:
            if bug_id in deprecatedIDs:
                continue

            bug_name = f"{proj}-{bug_id}"
            fl_res_dir = os.path.join(root, "DebugResult", "sf-evaluation", version, proj, bug_name)
            dataset_file = os.path.join(fl_res_dir, "dataset_for_fix.json")
            with open(dataset_file, "r") as f:
                dataset_for_fix = json.load(f)
            dataset[bug_name] = dataset_for_fix[0]

    with open(os.path.join(root, "DebugResult", "sf-evaluation", version, "dataset.json"), "w") as f:
        json.dump(dataset, f, indent=2)
