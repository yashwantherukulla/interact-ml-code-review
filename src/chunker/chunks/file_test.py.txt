from tree_sitter_languages import get_language, get_parser
import json
    
def generateAst(filePath, language):
    lang = get_language(language)
    if lang is None:
        return None
    
    parser = get_parser(language)

    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            content = file.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

    try:
        tree = parser.parse(bytes(content, 'utf-8'))
        return tree
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None
    
def node_to_dict(node):
    result = {
        "type": node.type,
        "start_point": node.start_point,
        "end_point": node.end_point,
        "children": [node_to_dict(child) for child in node.children]
    }
    return result
    
if __name__ == '__main__':
    tree = generateAst('./cloned_repos/regit/main.go', 'go')
    tree_dict = node_to_dict(tree.root_node)
    with open('./src/chunker/example_ast.json', 'w') as f:
        json.dump(tree_dict, f)