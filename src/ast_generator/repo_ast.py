import os
from ast_generator import generateAst, detectLanguage
from parse_checker import isParsable
import json

def node_to_dict(node):
    result = {
        "type": node.type,
        "start_point": node.start_point,
        "end_point": node.end_point,
        "children": [node_to_dict(child) for child in node.children]
    }
    return result

def process_directory(repo_path):
    asts_dir = os.path.join(repo_path, 'asts')
    os.makedirs(asts_dir, exist_ok=True)

    for root, dirs, files in os.walk(repo_path):
        if root.startswith(asts_dir):
            continue
        for file in files:
            filePath = os.path.join(root, file)
            if isParsable(filePath):
                language = detectLanguage(filePath)

                if language == 'unknown':
                    print(f"Unknown language for file: {filePath}")
                    return None

                ast = generateAst(filePath, language)
                ast_dict = node_to_dict(ast.root_node)

                # name of file is set here
                relative_path = os.path.relpath(filePath, repo_path)
                ast_file_name = relative_path.replace(os.path.sep, '_') + '.json'
                ast_file_path = os.path.join(asts_dir, ast_file_name)

                with open(ast_file_path, 'w') as ast_file:
                    json.dump(ast_dict, ast_file, indent=2)
            else:
                print(f"The file {filePath} does not appear to contain parsable code.")