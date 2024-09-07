def extract_chunks(self, file_path:str, language:str) -> List[ChunkNode]:
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        parser = tree_sitter.Parser()
        parser.set_language(self.languages[language])
        tree = parser.parse(bytes(content, 'utf8'))

        chunks = []
        self._traverse_tree(tree.root_node, None, chunks, content)
        return chunks