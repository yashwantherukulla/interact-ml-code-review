import unittest
import tempfile
from pathlib import Path
import msgpack
from chunk_extractor import ChunkExtractor
from tree_sitter_languages import get_language

class TestChunkExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for cache
        cls.temp_dir = tempfile.mkdtemp()
        cls.cache_dir = Path(cls.temp_dir) / "cache"
        cls.cache_dir.mkdir()

        # Get the Python language from py-sitter-languages
        cls.language = get_language("python")

        # Create a sample Python file
        cls.sample_file = Path(cls.temp_dir) / "sample.py"
        with cls.sample_file.open("w") as f:
            f.write("""
def example_function(name):
    if name == "Alice":
        return "Hello, Alice!"
    else:
        return "Hello, stranger!"
""")

        # Create the example AST file
        cls.ast_file = Path(cls.temp_dir) / "example_ast.msgpack"
        example_ast = {
            'type': 'module',
            'start_point': (0, 0),
            'end_point': (7, 0),
            'children': [
                {
                    'type': 'function_definition',
                    'start_point': (0, 0),
                    'end_point': (6, 0),
                    'children': [
                        {
                            'type': 'def',
                            'start_point': (0, 0),
                            'end_point': (0, 3)
                        },
                        {
                            'type': 'identifier',
                            'start_point': (0, 4),
                            'end_point': (0, 18)
                        },
                        {
                            'type': 'parameters',
                            'start_point': (0, 18),
                            'end_point': (0, 24),
                            'children': [
                                {
                                    'type': 'identifier',
                                    'start_point': (0, 19),
                                    'end_point': (0, 23)
                                }
                            ]
                        },
                        {
                            'type': 'block',
                            'start_point': (1, 4),
                            'end_point': (6, 0),
                            'children': [
                                {
                                    'type': 'if_statement',
                                    'start_point': (1, 4),
                                    'end_point': (5, 12),
                                    'children': [
                                        {
                                            'type': 'if',
                                            'start_point': (1, 4),
                                            'end_point': (1, 6)
                                        },
                                        {
                                            'type': 'comparison_operator',
                                            'start_point': (1, 7),
                                            'end_point': (1, 16)
                                        },
                                        {
                                            'type': 'block',
                                            'start_point': (2, 8),
                                            'end_point': (3, 21),
                                            'children': [
                                                {
                                                    'type': 'return_statement',
                                                    'start_point': (2, 8),
                                                    'end_point': (2, 19)
                                                }
                                            ]
                                        },
                                        {
                                            'type': 'else',
                                            'start_point': (3, 4),
                                            'end_point': (3, 8)
                                        },
                                        {
                                            'type': 'block',
                                            'start_point': (4, 8),
                                            'end_point': (5, 12),
                                            'children': [
                                                {
                                                    'type': 'return_statement',
                                                    'start_point': (4, 8),
                                                    'end_point': (4, 20)
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        with cls.ast_file.open("wb") as f:
            msgpack.pack(example_ast, f)

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        self.extractor = ChunkExtractor(self.language, str(self.cache_dir))

    def test_extract_chunks(self):
        # Test extracting chunks from the sample file
        ast = self.extractor.extract_chunks(str(self.sample_file), "python")
        
        # Check if the AST has the expected structure
        self.assertEqual(ast['type'], 'module')
        self.assertEqual(len(ast['children']), 1)
        self.assertEqual(ast['children'][0]['type'], 'function_definition')

    def test_caching(self):
        # Extract chunks for the first time
        self.extractor.extract_chunks(str(self.sample_file), "python")
        
        # Check if the cache file was created
        cache_files = list(self.cache_dir.glob("*.ast"))
        self.assertEqual(len(cache_files), 1)
        
        # Extract chunks again and check if the cached version is used
        cached_ast = self.extractor.extract_chunks(str(self.sample_file), "python")
        self.assertEqual(cached_ast['type'], 'module')

    def test_unsupported_language(self):
        # Test extracting chunks with an unsupported language
        with self.assertRaises(ValueError):
            self.extractor.extract_chunks(str(self.sample_file), "unsupported_lang")

if __name__ == '__main__':
    unittest.main()