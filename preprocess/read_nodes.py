import os

from llama_index.core import SimpleDirectoryReader

from preprocess.node_parser import JavaNodeParser


def get_methods_for_sbfl(path_manager, sbfl_res):
    src_path = os.path.join(path_manager.buggy_path, path_manager.src_prefix)
    reader = SimpleDirectoryReader(
        input_dir=src_path,
        recursive=True,
        required_exts=[".java"],
        encoding="utf-8"
    )
    documents = reader.load_data(show_progress=True)
    for doc in documents:
        doc.text = doc.text.replace("\r", "")

    # parse documents to code nodes according to the AST
    java_node_parser = JavaNodeParser.from_defaults()
    nodes = java_node_parser.get_nodes_from_documents(
        documents,
        [],
        show_progress=True,
        all_methods=True)
    
    all_nodes = [node for node in nodes if node.metadata["node_type"] == "method_node"]
    
    for node in all_nodes:
        file_path = node.metadata["file_path"]
        start_line = node.metadata["start_line"]
        end_line = node.metadata["end_line"]
        file_name = file_path.split("/")[-1]
        class_name = file_name.split(".")[0]
        
        if class_name in sbfl_res:
            for line_num, score in sbfl_res[class_name]:
                if start_line <= line_num <= end_line:
                    if "sbfl_score" not in node.metadata:
                        node.metadata["sbfl_score"] = score
                    else:
                        if score > node.metadata["sbfl_score"]:
                            node.metadata["sbfl_score"] = score
    
    filtered_nodes = [node for node in all_nodes if "sbfl_score" in node.metadata]
    sorted_nodes = sorted(filtered_nodes, key=lambda x: x.metadata["sbfl_score"], reverse=True)
    return sorted_nodes