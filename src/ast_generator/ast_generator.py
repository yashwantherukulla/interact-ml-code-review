import os
from tree_sitter_languages import get_language, get_parser
import logging
from .languages import languageExtensions


class AstGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detectLanguage(self, filePath: str) -> str:
        extension = os.path.splitext(filePath)[1][1:].lower()
        return languageExtensions.get(extension, "unknown")

    def generateAst(self, filePath: str, language: str):
        lang = get_language(language)
        if lang is None:
            self.logger.info(f"Language isn't supported of the file at: {filePath}")

        try:
            parser = get_parser(language)
            try:
                with open(filePath, "r", encoding="utf-8") as file:
                    content = file.read()
            except IOError as e:
                self.logger.info(f"Error reading file: {e}")

            try:
                tree = parser.parse(bytes(content, "utf-8"))
                return tree
            except Exception as e:
                self.logger.info(f"Error parsing file: {e}")
        except Exception as e:
            self.logger.info(f"Error getting parser for language at: {filePath}")
