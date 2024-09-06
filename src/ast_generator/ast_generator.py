import os
import tree_sitter 

languageExtensions = {
    '.erl': 'Erlang',
    '.lua': 'Lua',
    '.el': 'Elisp',
    'Makefile': 'Make',
    'Dockerfile': 'Dockerfile',
    'go.mod': 'Go Mod',
    '.ex': 'Elixir',
    '.elm': 'Elm',
    '.kt': 'Kotlin',
    '.pl': 'Perl',
    '.md': 'Markdown',
    '.yaml': 'YAML',
    '.m': 'Objective-C',
    '.sql': 'SQL',
    '.r': 'R',
    '.dot': 'DOT',
    '.hack': 'Hack',
    '.lisp': 'Common Lisp',
    '.sh': 'Bash',
    '.c': 'C',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.css': 'CSS',
    '.et': 'Embedded Template',
    '.go': 'Go',
    '.hs': 'Haskell',
    '.html': 'HTML',
    '.java': 'Java',
    '.js': 'JavaScript',
    '.json': 'JSON',
    '.jl': 'Julia',
    '.ml': 'OCaml',
    '.php': 'PHP',
    '.py': 'Python',
    '.ql': 'QL',
    '.regex': 'Regex',
    '.rb': 'Ruby',
    '.rs': 'Rust',
    '.scala': 'Scala',
    '.sqlite': 'SQLite',
    '.toml': 'TOML',
    '.tsq': 'TSQ',
    '.ts': 'TypeScript',
    '.rst': 'reStructuredText (RST)',
    '.hcl': 'HCL',
    '.f90': 'Fortran',
    '.f': 'Fixed-form Fortran'
}

def detectLanguage(filePath):
    extension = os.path.splitext(filePath)[1][1:].lower()
    return languageExtensions.get(extension, 'unknown')

def generateAst(filePath, language):
    parser = tree_sitter.Parser()
    try:
        #to do: setup the parser for the all languages above(external process)
        lang = tree_sitter.Language(f'path/to/{language}.so', language)
        parser.set_language(lang)
    except Exception as e:
        print(f"Error loading language {language}: {e}")
        return None

    with open(filePath, 'r') as file:
        content = file.read()

    tree = parser.parse(bytes(content, 'utf8'))
    return tree

#to do: need to put the file from fetcher here
filePath = "/content/drive/MyDrive/Colab Notebooks/csi_ml.py"
language = detectLanguage(filePath)

if language == 'unknown':
    print(f"Unknown language for file: {filePath}")
else:
    print(f"Detected language: {language}")

ast = generateAst(filePath, language)

if ast:
    print("AST generated successfully.")
    print(ast.root_node.sexp())
else:
    print("Failed to generate AST.")