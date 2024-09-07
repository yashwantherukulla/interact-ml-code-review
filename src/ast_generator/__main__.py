from .parse_checker import isParsable
from .ast_generator import detectLanguage, generateAst

if __name__ == "__main__":
    #to do: go through all the files
    filePath = '/content/drive/MyDrive/Colab Notebooks/pps3output.cpp'
    if isParsable(filePath):
        # print(f"The file {filePath} likely contains parsable code.")
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
    else:
        print(f"The file {filePath} does not appear to contain parsable code.")
    
    