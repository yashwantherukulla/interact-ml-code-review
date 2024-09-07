import json
from typing import Dict, List, Optional
from tree_sitter import Node
from .models import ChunkNode, ChunkGraph, ChunkType
from src.ast_generator.repo_ast import processDirectory

class ChunkExtractor:
    def __init__(self, ast_lookup_path: str):
        with open(ast_lookup_path, 'r') as f:
            self.ast_lookup = json.load(f)

    def extract_chunks(self, file_path: str) -> ChunkGraph:
        ast_file_path = self.ast_lookup[file_path]
        with open(ast_file_path, 'r') as f:
            ast = json.load(f)

        graph = ChunkGraph()
        self._process_node(ast, file_path, graph)
        return graph

    def _process_node(self, node: Dict, file_path: str, graph: ChunkGraph, parent: ChunkNode = None) -> ChunkNode:
        chunk_type = self._get_chunk_type(node)
        if chunk_type:
            chunk = ChunkNode(
                id=f"{file_path}:{node['start_point'][0]}:{node['end_point'][0]}",
                type=chunk_type,
                name=self._get_node_name(node),
                file_path=file_path,
                start_line=node['start_point'][0],
                end_line=node['end_point'][0],
                content=self._get_node_content(file_path, node),
                ast_node=node,
                parent=parent,
                imports=self._extract_imports(node) if chunk_type == ChunkType.FILE else []
            )
            graph.add_node(chunk)
            if parent:
                graph.add_edge(parent.id, chunk.id)

            for child in node.get('children', []):
                self._process_node(child, file_path, graph, chunk)

            return chunk

    def _get_chunk_type(self, node: Dict) -> Optional[ChunkType]:
        type_mapping = {
            'module': ChunkType.FILE,
            'class_definition': ChunkType.CLASS,
            'function_definition': ChunkType.FUNCTION,
        }
        return type_mapping.get(node['type'])

    def _get_node_name(self, node: Dict) -> str:
        if node['type'] in ['class_definition', 'function_definition']:
            for child in node['children']:
                if child['type'] == 'identifier':
                    return child['content']
        return node['type']

    def _get_node_content(self, file_path: str, node: Dict) -> str:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        return ''.join(lines[node['start_point'][0]:node['end_point'][0]+1])

    def _extract_imports(self, node: Dict) -> List[str]:
        imports = []
        for child in node.get('children', []):
            if child['type'] == 'import_statement':
                imports.append(child['content'])
            elif child['type'] == 'import_from_statement':
                imports.append(f"from {child['children'][1]['content']} import ...")
        return imports
    
if __name__ == '__main__':
    repoPath = './cloned_repos/regit'
    processDirectory(repoPath)
    extractor = ChunkExtractor(ast_lookup_path=repoPath + '/fileAstMap.json')
    graph = extractor.extract_chunks('src/chunker/chunk_extractor.py')
    graph.visualize_graph()