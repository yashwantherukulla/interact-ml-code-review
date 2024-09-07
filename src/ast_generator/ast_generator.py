import os
from tree_sitter_languages import get_language, get_parser

languageExtensions = {
    'erl': 'erlang',
    'lua': 'lua',
    'el': 'elisp',
    'Makefile': 'make',
    'Dockerfile': 'dockerfile',
    'go.mod': 'go mod',
    'ex': 'elixir',
    'elm': 'elm',
    'kt': 'kotlin',
    'pl': 'perl',
    'md': 'markdown',
    'yaml': 'yaml',
    'm': 'objective-c',
    'sql': 'sql',
    'r': 'r',
    'dot': 'dot',
    'hack': 'hack',
    'lisp': 'common lisp',
    'sh': 'bash',
    'c': 'c',
    'cs': 'c#',
    'cpp': 'c++',
    'css': 'css',
    'et': 'embedded template',
    'go': 'go',
    'hs': 'haskell',
    'html': 'html',
    'java': 'java',
    'js': 'javascript',
    'json': 'json',
    'jl': 'julia',
    'ml': 'ocaml',
    'php': 'php',
    'py': 'python',
    'ql': 'ql',
    'regex': 'regex',
    'rb': 'ruby',
    'rs': 'rust',
    'scala': 'scala',
    'sqlite': 'sqlite',
    'toml': 'toml',
    'tsq': 'tsq',
    'ts': 'typescript',
    'rst': 'restructuredtext (rst)',
    'hcl': 'hcl',
    'f90': 'fortran',
    'f': 'fixed-form fortran'
}

def detectLanguage(filePath):
    extension = os.path.splitext(filePath)[1][1:].lower()
    return languageExtensions.get(extension, 'unknown')

def generateAst(filePath, language):
    lang = get_language(language)
    if lang is None:
        return None
    
    parser = get_parser(language)

    with open(filePath, 'r') as file:
        content = file.read()

    tree = parser.parse(bytes(content, 'utf8'))
    return tree
