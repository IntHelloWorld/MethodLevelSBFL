import json
import os
import shutil
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
from functions.d4j import check_out, get_properties
from functions.line_parser import parse_test_report
from functions.MethodExtractor.java_method_extractor import JavaMethodExtractor
from functions.utils import run_cmd
from projects import SBF
from Utils.path_manager import PathManager

ALL_BUGS = SBF


def make_fix_dataset(path_manager: PathManager, sbfl_res):

    suspicious_methods = []
    java_method_extractor = JavaMethodExtractor()

    # check out the d4j project
    path_manager.logger.info("[checkout] start...")
    check_out(path_manager)

    # get bug specific information
    path_manager.logger.info("[get bug properties] start...")
    get_properties(path_manager)

    # extract trigger tests
    trigger_tests = {}
    for failed_test in path_manager.failed_test_names:
        test_class_name, test_method_name = failed_test.split("::")
        test_path = test_class_name.replace(".", "/") + ".java"
        test_java_file = os.path.join(
            path_manager.buggy_path,
            path_manager.test_prefix,
            test_path,
        )
        if not os.path.exists(test_java_file):
            raise FileNotFoundError(f"File {test_java_file} not found")

        with open(test_java_file, "r") as f:
            java_code = f.read()
        test_methods = java_method_extractor.get_java_methods(java_code)
        for test_method in test_methods:
            if test_method.name == test_method_name:
                # run single test
                cmd = f"{path_manager.bug_exec} test -t {failed_test} -w {path_manager.buggy_path}"
                run_cmd(cmd)
                test_report_file = os.path.join(path_manager.buggy_path, "failing_tests")
                with open(test_report_file, "r") as f:
                    text_lines = f.readlines()
                _, error_msg_lines = parse_test_report(text_lines)
                clean_lines = error_msg_lines[:2]
                test_info = {
                    "path": test_path,
                    "function_name": test_method_name,
                    "src": test_method.code,
                    "error_msg": "\n".join(error_msg_lines),
                    "clean_error_msg": "\n".join(clean_lines),
                }
                trigger_tests[failed_test] = test_info
    if len(trigger_tests) == 0:
        raise ValueError("No trigger test found")

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
                        "loc": os.path.join(path_manager.subproj, path_manager.src_prefix, pkg_name.replace(".", "/"), class_name + ".java"),
                        "method_signature": {'method_name': method.name},
                        "trigger_test": trigger_tests,
                        "buggy_code_comment": method.comment,
                    }
                    suspicious_methods.append(suspicious_method)

    with open(path_manager.dataset_file, "w") as f:
        json.dump(suspicious_methods, f, indent=2)

    shutil.rmtree(path_manager.buggy_path, ignore_errors=True)
    shutil.rmtree(path_manager.fixed_path, ignore_errors=True)


def sample_fix_dataset(all_bugs, top_k):
    version = "GrowingBugs"
    for i in range(1, top_k+1):
        dataset = {}
        for proj in all_bugs:
            bugIDs = all_bugs[proj][0]
            deprecatedIDs = all_bugs[proj][1]
            subproj = all_bugs[proj][2]
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
                if i <= len(dataset_for_fix):
                    dataset[bug_name] = dataset_for_fix[i-1]

        with open(os.path.join(root, "DebugResult", "sf-evaluation", version, f"dataset_rank_{i}.json"), "w") as f:
            json.dump(dataset, f, indent=2)
