import json
import os
from typing import Dict, List, Optional, Tuple
from .models import ChunkNode, ChunkGraph, ChunkType
from src.ast_generator.repo_ast import processDirectory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChunkExtractor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.ast_lookup_path = processDirectory(repo_path)
        try:
            with open(self.ast_lookup_path, 'r') as f:
                self.ast_lookup = json.load(f)
        except FileNotFoundError:
            logger.error(f"AST lookup file not found: {self.ast_lookup_path}")
            raise

    def extract_chunks(self, file_path: str) -> Optional[ChunkGraph]:
        if file_path not in self.ast_lookup:
            logger.warning(f"No AST found for file: {file_path}")
            return None

        ast_file_path = self.ast_lookup[file_path]
        try:
            with open(ast_file_path, 'r') as f:
                ast = json.load(f)
        except FileNotFoundError:
            logger.error(f"AST file not found: {ast_file_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in AST file: {ast_file_path}")
            return None

        graph = ChunkGraph()
        self._process_node(ast, file_path, graph)
        return graph

    def _process_node(self, node: Dict, file_path: str, graph: ChunkGraph, parent: ChunkNode = None) -> Optional[ChunkNode]:
        chunk_type = self._get_chunk_type(node)
        if chunk_type:
            try:
                chunk = ChunkNode(
                    id=f"{file_path}:{node['start_point'][0]}:{node['end_point'][0]}",
                    type=chunk_type,
                    file_path=file_path,
                    start_line=node['start_point'][0],
                    end_line=node['end_point'][0],
                    content=self._get_node_content(file_path, node),
                    ast_node=node,
                    parent=parent,
                    imports=self._extract_imports(file_path, node) if chunk_type == ChunkType.FILE else []
                )
                graph.add_node(chunk)
                if parent:
                    graph.add_edge(parent.id, chunk.id)

                if chunk_type == ChunkType.FILE:
                    self._extract_immediate_file_code(node, file_path, graph, chunk)

                for child in node.get('children', []):
                    self._process_node(child, file_path, graph, chunk)

                return chunk
            except KeyError as e:
                logger.error(f"Missing key in node: {e}")
                return None

    def _get_chunk_type(self, node: Dict) -> Optional[ChunkType]:
        type_mapping = {
            'module': ChunkType.FILE,
            'class_definition': ChunkType.CLASS,
            'function_definition': ChunkType.FUNCTION,
        }
        return type_mapping.get(node.get('type'))

    def _get_node_content(self, file_path: str, node: Dict) -> str:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            return ''.join(lines[node['start_point'][0]:node['end_point'][0]+1])
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return ""
        except IndexError:
            logger.error(f"Invalid line numbers in node: {node}")
            return ""

    def _extract_imports(self, file_path: str, node: Dict) -> List[str]:
        imports = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for child in node.get('children', []):
            if child.get('type') in ['import_statement', 'import_from_statement']:
                start_line = child['start_point'][0]
                end_line = child['end_point'][0]
                import_lines = lines[start_line:end_line+1]
                import_statement = ''.join(import_lines).strip()
                imports.append(import_statement)
        
        return imports

    def _extract_immediate_file_code(self, node: Dict, file_path: str, graph: ChunkGraph, parent: ChunkNode):
        immediate_code, ranges = self._get_immediate_file_code(node, file_path)
        if immediate_code.strip():
            name = "_".join([f"({start}_{end})" for start, end in ranges])
            immediate_chunk = ChunkNode(
                id=f"{file_path}:immediate:{name}",
                type=ChunkType.IMMEDIATE_CODE,
                file_path=file_path,
                start_line=ranges[0][0],
                end_line=ranges[-1][1],
                content=immediate_code,
                ast_node=node,
                parent=parent,
                imports=[]
            )
            graph.add_node(immediate_chunk)
            graph.add_edge(parent.id, immediate_chunk.id)

    def _get_immediate_file_code(self, node: Dict, file_path: str) -> Tuple[str, List[Tuple[int, int]]]:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        immediate_code_lines = []
        ranges = []
        current_line = node['start_point'][0]

        for child in node.get('children', []):
            if child['type'] in ['function_definition', 'class_definition']:
                if current_line < child['start_point'][0]:
                    immediate_code_lines.extend(lines[current_line:child['start_point'][0]])
                    ranges.append((current_line, child['start_point'][0] - 1))
                current_line = child['end_point'][0] + 1

        if current_line < node['end_point'][0] + 1:
            immediate_code_lines.extend(lines[current_line:node['end_point'][0]+1])
            ranges.append((current_line, node['end_point'][0]))

        return ''.join(immediate_code_lines), ranges

if __name__ == '__main__':
    repoPath = './cloned_repos/techBarista'
    extractor = ChunkExtractor(repoPath)
    graph = extractor.extract_chunks(os.path.join(repoPath, 'backend/main.py'))
    if graph:
        graph.export_to_json("./cloned_repos/techBarista/asts/chunks.json")
    else:
        logger.error("Failed to extract chunks")