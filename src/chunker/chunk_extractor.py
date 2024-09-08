import json
import os
from typing import Dict, List, Optional, Tuple
from .models import ChunkNode, ChunkGraph, ChunkType
from src.ast_generator.repo_ast import RepoAst
from src.ast_generator.ast_generator import AstGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChunkExtractor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        ast_generator = AstGenerator()
        repo_ast = RepoAst(ast_generator)
        self.ast_lookup_path = repo_ast.processDirectory(repo_path)
        try:
            with open(self.ast_lookup_path, 'r') as f:
                self.ast_lookup = json.load(f)
        except FileNotFoundError:
            logger.error(f"AST lookup file not found: {self.ast_lookup_path}")
            raise

    def extract_file_chunks(self, file_path: str) -> Optional[ChunkGraph]:
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

    def _process_node(self, node: Dict, file_path: str, graph: ChunkGraph, parent: Optional[ChunkNode] = None) -> Optional[ChunkNode]:
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
                    ast_node=node
                )
                graph.add_node(chunk)
                if parent:
                    graph.add_edge(parent.id, chunk.id)

                if chunk_type == ChunkType.FILE:
                    chunk.imports = self._extract_imports(file_path, node)
                    self._extract_immediate_file_code(node, file_path, graph, chunk)

                for child in node.get('children', []):
                    child_chunk = self._process_node(child, file_path, graph, chunk)
                    if child_chunk:
                        chunk.children.append(child_chunk)

                return chunk
            except KeyError as e:
                logger.error(f"Missing key in node: {e}")
                return None
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
        immediate_code_ranges = self._get_immediate_file_code(node, file_path)
        for start, end in immediate_code_ranges:
            immediate_chunk = ChunkNode(
                id=f"{file_path}:immediate:{start}_{end}",
                type=ChunkType.IMMEDIATE_CODE,
                file_path=file_path,
                start_line=start,
                end_line=end,
                content=self._get_node_content(file_path, {'start_point': [start, 0], 'end_point': [end, 0]}),
                ast_node=node
            )
            graph.add_node(immediate_chunk)
            graph.add_edge(parent.id, immediate_chunk.id)
            parent.children.append(immediate_chunk)

    def _get_immediate_file_code(self, node: Dict, file_path: str) -> List[Tuple[int, int]]:
        ranges = []
        current_line = node['start_point'][0]

        for child in node.get('children', []):
            if child['type'] in ['function_definition', 'class_definition']:
                if current_line < child['start_point'][0]:
                    ranges.append((current_line, child['start_point'][0] - 1))
                current_line = child['end_point'][0] + 1

        if current_line < node['end_point'][0] + 1:
            ranges.append((current_line, node['end_point'][0]))

        return ranges
    
    def extract_chunks(self, export_to_json=True):
        chunk_graphs = {}
        chunkGraphMap = {}  # {file_path: chunk_path}
        for file_path in self.ast_lookup.keys():
            graph = self.extract_file_chunks(file_path)
            if graph:
                chunk_graphs[file_path] = graph
                relative_path = os.path.relpath(file_path, self.repo_path)
                output_path = os.path.join(self.repo_path, "asts", relative_path.replace(os.path.sep, '_') + '-CHUNKS.json')
                chunkGraphMap[file_path] = output_path
        
        if export_to_json:
            os.makedirs(os.path.join(self.repo_path, "asts"), exist_ok=True)
            for file_path, graph in chunk_graphs.items():
                relative_path = os.path.relpath(file_path, self.repo_path)
                output_path = os.path.join(self.repo_path, "asts", relative_path.replace(os.path.sep, '_') + '-CHUNKS.json')
                graph.export_to_json(output_path)

            with open(os.path.join(self.repo_path, 'asts', 'chunkGraphMap.json'), 'w') as f:
                json.dump(chunkGraphMap, f, indent=2)

        return chunk_graphs

if __name__ == '__main__':
    repo_path = './cloned_repos/techBarista'
    extractor = ChunkExtractor(repo_path)
    chunk_graphs = extractor.extract_chunks()  # outputs to ./cloned_repos/techBarista/asts