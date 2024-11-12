import json
from difflib import unified_diff

from unidiff import PatchSet

dataset_file = "/root/APR/FLtools/MethodLevelSBFL/Evaluation/GrowingBug-sf.json"
sbs_file = "/root/APR/FLtools/MethodLevelSBFL/DebugResult/sf-evaluation/GrowingBugs/verbose_analysis.json"

with open(dataset_file, "r") as f:
    dataset = json.load(f)

with open(sbs_file, "r") as f:
    sbs = json.load(f)["should_be_success"]

for bug_name in sbs:
    buggy_code = dataset[bug_name]["buggy"]
    fixed_code = dataset[bug_name]["fix"]
    buggy_lines = buggy_code.split("\n")
    fixed_lines = fixed_code.split("\n")
    diff = list(unified_diff(buggy_lines, fixed_lines,
                fromfile='text1',
                tofile='text2',
                n=0))
    diff = [line.rstrip("\n")+"\n" for line in diff]
    print(''.join(diff))
    assert len(diff) != 0, "buggy file and fixed file are the same"
    hunks = PatchSet("".join(diff))[0]
    changed_points_b = set()
    for hunk in hunks:
        changed_points_b.add(hunk.source_start)
        changed_points_b.add(hunk.source_start + hunk.source_length - 1)
    changed_buggy_methods = []
