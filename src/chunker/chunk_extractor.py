from pathlib import Path
from tree_sitter import Language, Parser
import json
from chunk_node import ChunkNode
from typing import List
from tree_sitter_languages import get_language

class ChunkExtractor:
    def __init__(self, language: Language):
        self.parser = Parser()
        self.language = language
        self.parser.set_language(self.language)

    def extract_chunks(self, file_path: str, ast_path: str) -> List[ChunkNode]:
        with open(ast_path, 'r') as f:
            ast = json.load(f)

        with open(file_path, 'r') as f:
            file_content = f.readlines()

        return self._convert_to_chunk_nodes(ast, file_content)

    def _convert_to_chunk_nodes(self, ast, file_content: List[str]) -> List[ChunkNode]:
        def convert_node(node, parent=None):
            start_line, start_col = node['start_point']
            end_line, end_col = node['end_point']
            content = ''.join(file_content[start_line:end_line + 1])
            if end_line == start_line:
                content = content[start_col:end_col]
            else:
                content = content[start_col:] + ''.join(file_content[start_line + 1:end_line]) + file_content[end_line][:end_col]

            chunk_node = ChunkNode(
                id=node.get('id', None),
                type=node['type'],
                content=content,
                start_line=start_line,
                end_line=end_line,
                parent=parent
            )
            chunk_node.children = [convert_node(child, chunk_node) for child in node.get('children', [])]
            return chunk_node

        return [convert_node(node) for node in ast['children']]

if __name__ == '__main__':
    language = get_language('python')
    chunk_extractor = ChunkExtractor(language)
    chunks = chunk_extractor.extract_chunks('./src/chunker/example_py.py', './src/chunker/example_ast.json')
    for chunk in chunks:
        print(chunk)