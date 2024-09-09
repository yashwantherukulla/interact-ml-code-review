import json
import os
from typing import Dict, List, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import ChunkNode, ChunkGraph, ChunkType
from ..ast_generator.ast_generator import AstGenerator
from ..ast_generator.repo_ast import RepoAst

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkExtractor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        ast_generator = AstGenerator()
        repo_ast = RepoAst(ast_generator)
        self.ast_lookup_path = repo_ast.processDirectory(repo_path)
        self.ast_lookup = self._load_ast_lookup()

    def _load_ast_lookup(self) -> Dict[str, str]:
        try:
            with open(self.ast_lookup_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"AST lookup file not found: {self.ast_lookup_path}")
            raise

    def extract_file_chunks(self, file_path: str) -> Optional[ChunkGraph]:
        if file_path not in self.ast_lookup:
            logger.warning(f"No AST found for file: {file_path}")
            return None

        ast = self._load_ast(self.ast_lookup[file_path])
        if not ast:
            return None

        graph = ChunkGraph()
        self._process_node(ast, file_path, graph)
        
        if not graph.nodes:
            self._create_single_file_chunk(file_path, ast, graph)
        
        return graph

    def _load_ast(self, ast_file_path: str) -> Optional[Dict]:
        try:
            with open(ast_file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading AST file {ast_file_path}: {str(e)}")
        return None

    def _process_node(self, node: Dict, file_path: str, graph: ChunkGraph, parent_id: Optional[str] = None) -> Optional[str]:
        chunk_type = self._get_chunk_type(node)
        if chunk_type:
            chunk = self._create_chunk(node, file_path, chunk_type)
            graph.add_node(chunk)
            if parent_id:
                graph.add_edge(parent_id, chunk.id)

            if chunk_type == ChunkType.FILE:
                chunk = chunk._replace(imports=self._extract_imports(file_path, node))
                graph.nodes[chunk.id] = chunk
                self._extract_immediate_file_code(node, file_path, graph, chunk.id)

            for child in node.get('children', []):
                child_id = self._process_node(child, file_path, graph, chunk.id)
                if child_id:
                    graph.add_edge(chunk.id, child_id)

            return chunk.id
        else:
            for child in node.get('children', []):
                self._process_node(child, file_path, graph, parent_id)
        return None

    def _create_chunk(self, node: Dict, file_path: str, chunk_type: ChunkType) -> ChunkNode:
        return ChunkNode(
            id=f"{file_path}:{node['start_point'][0]}:{node['end_point'][0]}",
            type=chunk_type,
            file_path=file_path,
            start_line=node['start_point'][0],
            end_line=node['end_point'][0],
            content=self._get_node_content(file_path, node)
        )

    def _create_single_file_chunk(self, file_path: str, ast: Dict, graph: ChunkGraph) -> None:
        chunk = ChunkNode(
            id=f"{file_path}:entire_file",
            type=ChunkType.FILE,
            file_path=file_path,
            start_line=1,
            end_line=self._get_file_line_count(file_path),
            content=self._get_file_content(file_path)
        )
        graph.add_node(chunk)

    @staticmethod
    def _get_chunk_type(node: Dict) -> Optional[ChunkType]:
        return {
            'module': ChunkType.FILE,
            'class_definition': ChunkType.CLASS,
            'function_definition': ChunkType.FUNCTION,
        }.get(node.get('type'))

    def _get_node_content(self, file_path: str, node: Dict) -> str:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            return ''.join(lines[node['start_point'][0]:node['end_point'][0]+1])
        except (FileNotFoundError, IndexError) as e:
            logger.error(f"Error reading node content from {file_path}: {str(e)}")
        return ""

    def _get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        return ""

    def _get_file_line_count(self, file_path: str) -> int:
        try:
            with open(file_path, 'r') as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        return 0

    def _extract_imports(self, file_path: str, node: Dict) -> List[str]:
        imports = []
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for child in node.get('children', []):
                if child.get('type') in ['import_statement', 'import_from_statement']:
                    start_line, end_line = child['start_point'][0], child['end_point'][0]
                    imports.append(''.join(lines[start_line:end_line+1]).strip())
        except FileNotFoundError:
            logger.error(f"File not found while extracting imports: {file_path}")
        return imports

    def _extract_immediate_file_code(self, node: Dict, file_path: str, graph: ChunkGraph, parent_id: str) -> None:
        for start, end in self._get_immediate_file_code(node):
            immediate_chunk = ChunkNode(
                id=f"{file_path}:immediate:{start}_{end}",
                type=ChunkType.IMMEDIATE_CODE,
                file_path=file_path,
                start_line=start,
                end_line=end,
                content=self._get_node_content(file_path, {'start_point': [start, 0], 'end_point': [end, 0]})
            )
            graph.add_node(immediate_chunk)
            graph.add_edge(parent_id, immediate_chunk.id)

    @staticmethod
    def _get_immediate_file_code(node: Dict) -> List[Tuple[int, int]]:
        ranges = []
        current_line = node['start_point'][0]

        for child in node.get('children', []):
            if child['type'] in ['function_definition', 'class_definition']:
                if current_line < child['start_point'][0]:
                    ranges.append((current_line, child['start_point'][0] - 1))
                current_line = child['end_point'][0] + 1

        if current_line < node['end_point'][0]:
            ranges.append((current_line, node['end_point'][0]))

        return ranges
    
    def extract_chunks(self, export_to_json: bool = True) -> Dict[str, ChunkGraph]:
        chunk_graphs = {}
        chunkGraphMap = {}

        def process_file(file_path: str) -> Optional[Tuple[str, ChunkGraph, str]]:
            graph = self.extract_file_chunks(file_path)
            if graph:
                relative_path = os.path.relpath(file_path, self.repo_path)
                output_path = os.path.join(self.repo_path, "asts", relative_path.replace(os.path.sep, '_') + '-CHUNKS.json')
                return file_path, graph, output_path
            return None

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file, file_path) for file_path in self.ast_lookup]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    file_path, graph, output_path = result
                    chunk_graphs[file_path] = graph
                    chunkGraphMap[file_path] = output_path
        
        if export_to_json:
            os.makedirs(os.path.join(self.repo_path, "asts"), exist_ok=True)
            for file_path, graph in chunk_graphs.items():
                output_path = chunkGraphMap[file_path]
                self._export_graph_to_json(graph, output_path)

            with open(os.path.join(self.repo_path, 'asts', 'chunkGraphMap.json'), 'w') as f:
                json.dump(chunkGraphMap, f, indent=2)

        return chunk_graphs

    @staticmethod
    def _export_graph_to_json(graph: ChunkGraph, file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump(graph.to_dict(), f, indent=2)

def main() -> None:
    repo_path = './cloned_repos/techBarista'
    try:
        extractor = ChunkExtractor(repo_path)
        chunk_graphs = extractor.extract_chunks()
        logger.info(f"Successfully processed {len(chunk_graphs)} files")
    except Exception as e:
        logger.error(f"An error occurred during chunk extraction: {str(e)}")

if __name__ == '__main__':
    main()