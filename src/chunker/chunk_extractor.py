from typing import List
from tree_sitter import Language, Parser
from chunk_node import ChunkNode
from tree_sitter_languages import get_language
import os

class ChunkExtractor:
    def __init__(self, language: Language):
        self.parser = Parser()
        self.language = language
        self.parser.set_language(self.language)

    def extract_chunks(self, file_path: str) -> List[ChunkNode]:
        with open(file_path, 'r') as f:
            content = f.read()

        parser = Parser()
        parser.set_language(self.language)
        tree = parser.parse(bytes(content, 'utf8'))

        chunks = []
        root_chunk = ChunkNode(
            id=f"file_{os.path.basename(file_path)}",
            type='file',
            content=content,
            start_line=0,
            end_line=len(content.splitlines()),
            parent=None
        )
        chunks.append(root_chunk)
        self._traverse_tree(tree.root_node, root_chunk, chunks, content)
        return chunks

    def _traverse_tree(self, node, parent, chunks, content):
        if node.type in ['function_definition', 'class_definition']:
            node_name = self._get_node_name(node)
            parent_name = parent.id if parent else "root"
            chunk_id = f"{parent_name}_{node_name}_{node.start_point[0]}_{node.end_point[0]}"
            chunk = ChunkNode(
                id=chunk_id,
                type='function' if node.type == 'function_definition' else 'class',
                content=content[node.start_byte:node.end_byte],
                start_line=node.start_point[0],
                end_line=node.end_point[0],
                parent=parent
            )

            chunks.append(chunk)
            parent = chunk

        for child in node.children:
            self._traverse_tree(child, parent, chunks, content)

    def _get_node_name(self, node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf-8')
        return "Unknown"

if __name__ == '__main__':
    language = get_language('python')
    chunk_extractor = ChunkExtractor(language)
    chunks = chunk_extractor.extract_chunks('./src/chunker/test.py')
    print(f"Extracted {len(chunks)} chunks:")

    output_dir = './src/chunker/chunks'
    os.makedirs(output_dir, exist_ok=True)
    
    for chunk in chunks:
        with open(f'./src/chunker/chunks/{chunk.id}.txt', 'w') as f:
            f.write(chunk.content)
        print(chunk)