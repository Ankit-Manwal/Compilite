#!/usr/bin/env python3

"""
Simple script to run the compiler on a source file.
Usage: python compile.py <source_file>
"""

import sys
from compiler.environment import CompilerEnvironment
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.code_generator import IntermediateCodeGenerator, TargetCodeGenerator

def compile_file(source_file: str, debug: bool = False) -> bool:
    """
    Compile a source file through all compilation phases.
    
    Args:
        source_file: Path to the source file
        debug: Enable debug mode
        
    Returns:
        bool: True if compilation succeeded, False otherwise
    """
    try:
        # Read source file
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        # Set up compilation environment
        with CompilerEnvironment(debug_mode=debug) as env:
            print(f"\nCompiling {source_file}...")
            
            # 1. Lexical Analysis
            print("\n1. Performing lexical analysis...")
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            # 2. Parsing
            print("\n2. Performing syntax analysis...")
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 3. Semantic Analysis
            print("\n3. Performing semantic analysis...")
            analyzer = SemanticAnalyzer(ast)
            analyzer.analyze()
            
            # 4. Intermediate Code Generation
            print("\n4. Generating intermediate code...")
            int_generator = IntermediateCodeGenerator(ast)
            intermediate_code = int_generator.generate()
            
            # Save intermediate code
            intermediate_file = env.get_output_path('intermediate.txt')
            with open(intermediate_file, 'w') as f:
                for instr in intermediate_code:
                    f.write(instr + '\n')
            print(f"Intermediate code written to: {intermediate_file}")
            
            # 5. Target Code Generation
            print("\n5. Generating target code...")
            target_generator = TargetCodeGenerator(intermediate_code)
            target_code = target_generator.generate()
            
            # Save target code
            target_file = env.get_output_path('output.asm')
            with open(target_file, 'w') as f:
                for instr in target_code:
                    f.write(instr + '\n')
            print(f"Assembly code written to: {target_file}")
            
            print("\nCompilation completed successfully!")
            return True
            
    except Exception as e:
        print(f"\nError during compilation: {str(e)}", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python compile.py <source_file> [--debug]")
        sys.exit(1)
    
    source_file = sys.argv[1]
    debug_mode = "--debug" in sys.argv
    
    success = compile_file(source_file, debug_mode)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 