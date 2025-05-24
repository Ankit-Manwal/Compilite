#!/usr/bin/env python3

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.code_generator import IntermediateCodeGenerator, TargetCodeGenerator

def compile_file(source_file, intermediate_file='intermediate.txt', target_file='target.txt'):
    """
    Compiles a source file through all phases of compilation:
    1. Lexical Analysis
    2. Parsing
    3. Semantic Analysis
    4. Intermediate Code Generation
    5. Target Code Generation
    
    Args:
        source_file (str): Path to the source file
        intermediate_file (str): Path to save intermediate code
        target_file (str): Path to save target code
    """
    print("Starting compilation process...")
    
    # Read source file
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found")
        return
    except Exception as e:
        print(f"Error reading source file: {e}")
        return
    
    try:
        # Print source code
        print("\nSource Code:")
        print('=' * 40)
        print(source_code)
        print('=' * 40)
        
        # Phase 1: Lexical Analysis
        print("\n1. Lexical Analysis")
        print('=' * 40)
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        print("Tokens:")
        for token in tokens:
            print(f"Type: {token.type}, Value: {token.value}")
        print('=' * 40)
        print("Lexical analysis completed successfully")
        
        # Phase 2: Parsing
        print("\n2. Parsing")
        print('=' * 40)
        parser = Parser(tokens)
        ast = parser.parse()
        print("Abstract Syntax Tree:")
        print_ast(ast, indent=0)
        print('=' * 40)
        print("Parsing completed successfully")
        
        # Phase 3: Semantic Analysis
        print("\n3. Semantic Analysis")
        semantic_analyzer = SemanticAnalyzer(ast)
        semantic_analyzer.analyze()
        print("Semantic analysis completed successfully")
        
        # Phase 4: Intermediate Code Generation
        print("\n4. Intermediate Code Generation")
        print('=' * 40)
        intermediate_generator = IntermediateCodeGenerator(ast)
        intermediate_code = intermediate_generator.generate()
        
        # Save and print intermediate code
        with open(intermediate_file, 'w') as f:
            for instruction in intermediate_code:
                f.write(instruction + '\n')
        print(f"Intermediate code saved to {intermediate_file}")
        print("\nIntermediate Code:")
        for instruction in intermediate_code:
            print(instruction)
        print('=' * 40)
        
        # Phase 5: Target Code Generation
        print("\n5. Target Code Generation")
        print('=' * 40)
        target_generator = TargetCodeGenerator(intermediate_code)
        target_code = target_generator.generate()
        
        # Save and print target code
        with open(target_file, 'w') as f:
            for instruction in target_code:
                f.write(instruction + '\n')
        print(f"Target code saved to {target_file}")
        print("\nTarget Code:")
        for instruction in target_code:
            print(instruction)
        print('=' * 40)
        
        print("\nCompilation completed successfully!")
        
    except Exception as e:
        print(f"\nError during compilation: {e}")
        raise

def print_ast(node, indent=0):
    """Helper function to print AST in a readable format"""
    indent_str = "  " * indent
    
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
        return
    
    if not isinstance(node, dict):
        print(f"{indent_str}{node}")
        return
    
    print(f"{indent_str}Node Type: {node['type']}")
    for key, value in node.items():
        if key == 'type':
            continue
        if isinstance(value, (dict, list)):
            print(f"{indent_str}{key}:")
            print_ast(value, indent + 1)
        else:
            print(f"{indent_str}{key}: {value}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python run_compiler.py <source_file>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    compile_file(source_file) 