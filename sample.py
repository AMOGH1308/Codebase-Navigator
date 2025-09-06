import tree_sitter_python
from tree_sitter import Parser

parser = Parser()
lang=tree_sitter_python.language()
print(type(lang))