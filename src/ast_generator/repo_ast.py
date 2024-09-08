import os
from .ast_generator import AstGenerator
import json
import logging

class RepoAst:
    def __init__(self, ast_generator: AstGenerator):
        self.logger = logging.getLogger(__name__)
        self.ast_generator = ast_generator

    def nodeToDict(self, node):
        result = {
            "type": node.type,
            "start_point": node.start_point,
            "end_point": node.end_point,
            "children": [self.nodeToDict(child) for child in node.children]
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
                language = AstGenerator.detectLanguage(filePath)
                if language == 'unknown':
                    print(f"Skipping file with unknown language: {filePath}")
                    continue

                ast = AstGenerator.generateAst(filePath, language)
                if ast is None:
                    print(f"Failed to generate AST for file: {filePath}")
                    continue

                astDict = AstGenerator.nodeToDict(ast.root_node)

                relative_path = os.path.relpath(filePath, repoPath)
                astFileName = relative_path.replace(os.path.sep, '_') + '.json'
                astFilePath = os.path.join(astsDir, astFileName)

            with open(astFilePath, 'w') as astFile:
                json.dump(astDict, astFile, indent=2)
            
                fileAstMap[filePath] = astFilePath
        
        with open(mappingFilePath, 'w') as mapFile:
            json.dump(fileAstMap, mapFile, indent=2)

        return mappingFilePath