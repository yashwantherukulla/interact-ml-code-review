import os
import json
from .ast_generator import generateAst, detectLanguage

def nodeToDict(node):
    result = {
        "type": node.type,
        "start_point": node.start_point,
        "end_point": node.end_point,
        "children": [nodeToDict(child) for child in node.children]
    }
    return result

def processDirectory(repoPath):
    astsDir = os.path.join(repoPath, 'asts')
    mappingFilePath = os.path.join(astsDir, 'fileAstMap.json')
    os.makedirs(astsDir, exist_ok=True)

    fileAstMap = {}
    for root, dirs, files in os.walk(repoPath):
        if root.startswith(astsDir):
            continue

        for file in files:
            filePath = os.path.join(root, file)
            language = detectLanguage(filePath)
            if language == 'unknown':
                print(f"Skipping file with unknown language: {filePath}")
                continue

            ast = generateAst(filePath, language)
            if ast is None:
                print(f"Failed to generate AST for file: {filePath}")
                continue

            astDict = nodeToDict(ast.root_node)

            relative_path = os.path.relpath(filePath, repoPath)
            astFileName = relative_path.replace(os.path.sep, '_') + '.json'
            astFilePath = os.path.join(astsDir, astFileName)

            with open(astFilePath, 'w') as astFile:
                json.dump(astDict, astFile, indent=2)
            
            fileAstMap[filePath] = astFilePath
    
    with open(mappingFilePath, 'w') as mapFile:
        json.dump(fileAstMap, mapFile, indent=2)

    return mappingFilePath