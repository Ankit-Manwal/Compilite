"""
A compiler for a C-like language that generates x86-like assembly code.
"""

from .lexer import Lexer
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from .code_generator import IntermediateCodeGenerator, TargetCodeGenerator

__all__ = [
    'Lexer',
    'Parser',
    'SemanticAnalyzer',
    'IntermediateCodeGenerator',
    'TargetCodeGenerator'
]