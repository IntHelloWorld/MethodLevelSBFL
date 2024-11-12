import os
import re
from typing import Dict, List

from Utils.path_manager import PathManager


def parse_sbfl(sbfl_file) -> Dict[str, List[int]]:
    """
    Parse the SBFL result from line level to method level.
    e.g.:
        org.jfree.chart.plot$CategoryPlot#CategoryPlot():567;0.2581988897471611
        org.jfree.chart.plot$CategoryPlot#CategoryPlot():568;0.2581988897471611
        
        ==>
        
        {
            "CategoryPlot": [(567, 0.2581988897471611), (568, 0.2581988897471611)]
        }
    """
    res = {}
    with open(sbfl_file, "r") as f:
        line = f.readline() # skip the first line
        line = f.readline().strip("\n")
        while line:
            full_name, method_name, line_num, score = re.split(r"[#:;]", line)
            class_name = full_name.split("$")[1]
            
            if score == "0.0":
                break

            try:
                res[class_name].append((int(line_num), float(score)))
            except:
                res[class_name] = [(int(line_num), float(score))]
            line = f.readline().strip("\n")
    return res


def parse_sbfl_version_2(sbfl_file):
    """
    Parse the SBFL result from line level to method level.
    e.g.:
        com.fasterxml.aalto.in$XmlScanner#reportPrologUnexpChar(boolean,int,java.lang.String):1356;1.0
        com.fasterxml.aalto.in$XmlScanner#reportPrologUnexpChar(boolean,int,java.lang.String):1358;1.0
        com.fasterxml.aalto.in$XmlScanner#throwUnexpectedChar(int,java.lang.String):1493;1.0
        com.fasterxml.aalto.in$XmlScanner#throwUnexpectedChar(int,java.lang.String):1496;1.0
        com.fasterxml.aalto.in$XmlScanner#reportInputProblem(java.lang.String):1333;0.7071067811865475

        ==>

        [
            [
                ("com.fasterxml.aalto.in", "XmlScanner", "reportPrologUnexpChar", [1356, 1358]),
                ("com.fasterxml.aalto.in", "XmlScanner", "throwUnexpectedChar", [1493, 1496])
            ],
            [
                ("com.fasterxml.aalto.in", "XmlScanner", "reportInputProblem", [1333])
            ]
        ]
    """
    res = []
    last_score = ""
    with open(sbfl_file, "r") as f:
        line = f.readline() # skip the first line
        line = f.readline().strip("\n")
        while line:
            match = re.match(r"^(.*?)\$(.*?)\#(.*?)\((.*?)\):(\d+);(.*?)$", line)
            if match:
                pkg_name, class_name, method_name, _, line_num, score = match.groups()
            else:
                raise ValueError(f"Failed to parse line: {line}")
            if score != last_score:
                res.append([])
            if score == "0.0":
                break

            if len(res[-1]) == 0:
                res[-1].append((pkg_name, class_name, method_name, [int(line_num)]))
            elif res[-1][-1][1] != class_name or res[-1][-1][2] != method_name:
                res[-1].append((pkg_name, class_name, method_name, [int(line_num)]))
            else:
                res[-1][-1][3].append(int(line_num))

            last_score = score
            line = f.readline().strip("\n")
    return res


def get_all_sbfl_res(path_manager: PathManager):
    sbfl_names = ["tarantula","ochiai","jaccard","ample","ochiai2","dstar"]
    sbfl_files = []
    for name in sbfl_names:
        sbfl_files.append(os.path.join(
            path_manager.root_path,
            "SBFL",
            "results",
            path_manager.project,
            path_manager.bug_id,
            f"{name}.ranking.csv"
        ))
    
    sbfl_reses = []
    for sbfl_file in sbfl_files:
        sbfl_reses.append(parse_sbfl(sbfl_file))
    return sbfl_reses
