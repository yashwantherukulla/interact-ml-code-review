import os
import magic
import chardet
import re

def isParsable(filePath):
    try:
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"File not found: {filePath}")

        mime = magic.Magic(mime=True)
        fileType = mime.from_file(filePath)
        
        codeMimeTypes = ['text/x-script.python', 'text/x-python', 'text/x-c', 'text/x-c++', 'text/x-java-source', 'text/javascript', 
                         'application/javascript', 'text/x-php', 'text/x-ruby', 'text/x-perl', 'text/x-shellscript', 'text/x-scala-source', 
                         'text/x-go', 'text/x-rustsrc', 'text/x-haskell', 'text/x-kotlin', 'text/x-swift', 'text/x-csharp', 
                         'text/x-typescript', 'text/x-matlab', 'application/x-executable', 'text/x-msdos-batch', 'text/x-powershell', 
                         'text/x-lua', 'text/x-lisp', 'text/x-sql', 'text/x-r', 'text/x-fortran', 'text/x-asm', 'text/x-makefile', 
                         'text/x-groovy', 'text/x-java']

        if fileType not in codeMimeTypes:
            return False

        with open(filePath, 'rb') as file:
            content = file.read(4096)
        result = chardet.detect(content)
        encoding = result['encoding']

        decodedContent = content.decode(encoding)

        codeIndicators = [r'\bfunction\s+\w+\s*\(', r'\bclass\s+\w+', r'\bimport\s+\w+', r'\bpackage\s+\w+',
                          r'#include\s+[<"]', r'\bpublic\s+static\s+void\s+main', r'\bdef\s+\w+\s*\(', r'\bif\s*\(.+\)\s*{',
                          r'\bfor\s*\(.+\)\s*{', r'\bwhile\s*\(.+\)\s*{', r'^\s*#!.*python', r'^\s*#!.*node',
                          r'^\s*#!.*ruby', r'^\s*#!.*perl', r'^\s*#!.*bash', r'<\?php', r'<\?=', r'using\s+namespace', r'^\s*@import', 
                          r'^\s*SELECT.*FROM', r'^\s*CREATE\s+TABLE', r'^\s*public\s+class', r'^\s*private\s+class', r'^\s*interface\s+\w+',
                          r'\bfunc\s+\w+\(', r'\bfn\s+\w+\(', r'\blet\s+\w+\s*=', r'\bconst\s+\w+\s*=',
                          r'\bvar\s+\w+\s*=', r'\bmodule\s+\w+', r'\bdef\s+\w+\s*\(', r'\bfor\s+\w+\s+in\s+', r'\bwhile\s+.+:', 
                          r'\bif\s+.+:', r'\belif\s+.+:', r'\belse:', r'\breturn\s+', r'\bprint\s*\(', r'\binput\s*\(', 
                          r'=\s*input\s*\(', r'\bwith\s+.+\s+as\s+']
        
        for pattern in codeIndicators:
            if re.search(pattern, decodedContent, re.MULTILINE | re.IGNORECASE):
                return True
        
        lines = decodedContent.split('\n')
        if len(lines) > 1:
            if all(',' in line for line in lines[:10]):  # Check first 10 lines for CSV
                return False
            if all('\t' in line for line in lines[:10]):  # Check first 10 lines for TSV
                return False

        return any(indicator in decodedContent for indicator in codeIndicators)

    except FileNotFoundError as e:
        print(f"File error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False