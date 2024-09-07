class ChunkExtractor:
    def __init__(self):
        # self.ALL_LANGUAGES = [
        #     'bash',
        #     'c',
        #     'c-sharp',
        #     'cpp',
        #     'css',
        #     'go',
        #     'html',
        #     'java',
        #     'javascript',
        #     'jsdoc',
        #     'json',
        #     'julia',
        #     'ocaml',
        #     'php',
        #     'python',
        #     'ql',
        #     'regex',
        #     'rst',
        #     'ruby',
        #     'rust',
        #     'scala',
        #     'toml',
        #     'typescript',
        #     ]
        
    # def _setup_languages(self):
        # removed the following as they were for older versions of tree-sitter
        # cache_dir = "./misc/py_sitter/cache"
        # build_dir = os.path.join(cache_dir, "build")
        # os.makedirs(build_dir, exist_ok=True)

        # for language in self.ALL_LANGUAGES:
        #     repo_dir = os.path.join(cache_dir, f"tree-sitter-{language}")
        #     if not os.path.exists(repo_dir):
        #         subprocess.run(f"git clone https://github.com/tree-sitter/tree-sitter-{language} {repo_dir}", shell=True, check=True)

        #     so_file = os.path.join(build_dir, f"{language}.so")
        #     if not os.path.exists(so_file):
        #         Language.build_library(so_file, [repo_dir])

        # self.languages = {language: Language(os.path.join(build_dir, f"{language}.so"), language) for language in self.ALL_LANGUAGES}
        
        

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
    
    def _traverse_tree(self, node, parent, chunks, content):
        if node.type in ['function_definition', 'class_definition']:
            chunk = ChunkNode(
                id = f"{node.type}_{node.start_point[0]}_{node.end_point[0]}",
                type = 'function' if node.type == 'function_definition' else 'class',
                name = self._get_node_name(node),
                content = content[node.start_byte:node.end_byte],
                start_line = node.start_point[0],
                end_line = node.end_point[0],
                parent = parent
            )

            chunks.append(chunk)
            parent = chunk

        for child in node.children:
            self._traverse_tree(child, parent, chunks, content)
    
    def _get_node_name(self, node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decoder('utf-8')
        return "Unknown"