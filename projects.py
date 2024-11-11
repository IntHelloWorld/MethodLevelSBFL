import os
import shutil

from SBFL.runMultiprocess_GrowingBugs import projDict

ALL_BUGS = projDict

SBF = {
    "Closure": ([44, 51, 55, 61, 101, 119, 159, 160], [], "None"),
    "Codec": ([4], [], "None"),
    "Compress": ([13, 39], [], "None"),
    "Csv": ([1, 10], [], "None"),
    "Imaging": ([3, 4, 6, 11, 14], [], "None"),
    "JacksonDatabind": ([1, 8, 9, 12, 16, 17, 19, 24, 33, 35, 42, 46, 125], [], "None"),
    "JacksonXml": ([3], [], "None"),
    "Mockito": ([13, 34], [], "None"),
    "Jsoup": ([8, 26, 51, 53, 70, 72], [], "None"),
    "HttpClient5": ([5], [], "httpclient5"),
    "Pdfbox_pdfbox": ([1, 3], [], "pdfbox"),
    "JavaClassmate": ([1, 2], [], "None"),
    "Woodstox": ([3, 4, 5], [], "None"),
    "MetaModel_core": ([3], [], "core"),
    "Mrunit": ([1], [], "None"),
    "Zip4j": ([2, 3, 5, 8], [], "None"),
    "Jdbm3": ([3], [], "None"),
    "Restfixture": ([2], [], "None"),
    "Jcabi_http": ([2, 13], [], "None"),
}

def delete_deprecated():
    projects_dir = "/home/qyh/projects/GarFL/Projects"
    for version in ALL_BUGS:
        for proj in ALL_BUGS[version]:
            for bug_id in ALL_BUGS[version][proj][1]:
                bug_dir = os.path.join(projects_dir, proj, str(bug_id))
                if os.path.exists(bug_dir):
                    print(f"Delete {bug_dir}")
                    shutil.rmtree(bug_dir)

def statistic_bugs():
    for version in ALL_BUGS:
        print(f"Version: {version}")
        print("PROJECT, ALL, Deprecated, Bugs")
        for proj in ALL_BUGS[version]:
            all = len(ALL_BUGS[version][proj][0])
            deprecated = len(ALL_BUGS[version][proj][1])
            print(f"{proj}, {all}, {deprecated}, {all-deprecated}")

def statistic_methods():
    import json
    from pathlib import Path
    
    results = []
    root_path = Path(__file__).resolve().parents[0].as_posix()
    stores_dir = os.path.join(root_path, "Stores", "codeqwen-1_5-7B")
    for version in ALL_BUGS:
        for proj in ALL_BUGS[version]:
            for bug_id in ALL_BUGS[version][proj][0]:
                if bug_id in ALL_BUGS[version][proj][1]:
                    continue
                doc_store = os.path.join(stores_dir, proj, "docstore.json")
                method_nodes = json.load(open(doc_store, "r"))
                results.append(f"{proj}: {len(method_nodes['docstore/data'])}")
                break
    print(results)

if __name__ == "__main__":
    # delete_deprecated()
    # statistic_bugs()
    statistic_methods()
