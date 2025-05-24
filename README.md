# Simple C-like Language Compiler

A compiler implementation for a C-like programming language, written in Python. The compiler performs lexical analysis, parsing, semantic analysis, and generates both intermediate code and x86 assembly output.

## Features

- Lexical analysis with support for:
  - Keywords (if, while, int, float, etc.)
  - Operators (+, -, *, /, ==, etc.)
  - Numbers and string literals
  - Comments (single and multi-line)

- Parsing support for:
  - Function declarations
  - Variable declarations
  - Control flow statements (if-else, while)
  - Expressions (arithmetic, logical, assignment)

- Semantic analysis:
  - Type checking
  - Scope management
  - Symbol table tracking

- Code generation:
  - Three-address code (TAC) intermediate representation
  - x86 assembly output

## Requirements

- Python 3.7 or higher
- Operating System: Windows/Linux/MacOS

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
compiler/
├── __init__.py
├── lexer.py          # Tokenization
├── parser.py         # Syntax analysis
├── semantic_analyzer.py  # Type checking and validation
├── symbol_table.py   # Symbol management
├── code_generator.py # Code generation
└── environment.py    # Compilation environment

build/               # Generated during compilation
├── temp/           # Temporary files
└── output/         # Compiled outputs
```

## Usage

1. Create a source file (e.g., `example.c`):
```c
int main() {
    int x = 10;
    while (x > 0) {
        print(x);
        x = x - 1;
    }
    return 0;
}
```

2. Run the compiler:
```python
from compiler.environment import CompilerEnvironment
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.code_generator import IntermediateCodeGenerator, TargetCodeGenerator

# Read source file
with open('example.c', 'r') as f:
    source_code = f.read()

# Set up compilation environment
with CompilerEnvironment(debug_mode=True) as env:
    # 1. Lexical Analysis
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    # 2. Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    
    # 3. Semantic Analysis
    analyzer = SemanticAnalyzer(ast)
    analyzer.analyze()
    
    # 4. Intermediate Code Generation
    int_generator = IntermediateCodeGenerator(ast)
    intermediate_code = int_generator.generate()
    
    # Save intermediate code
    with open(env.get_output_path('intermediate.txt'), 'w') as f:
        for instr in intermediate_code:
            f.write(instr + '\n')
    
    # 5. Target Code Generation
    target_generator = TargetCodeGenerator(intermediate_code)
    target_code = target_generator.generate()
    
    # Save target code
    with open(env.get_output_path('output.asm'), 'w') as f:
        for instr in target_code:
            f.write(instr + '\n')
```

## Output Files

- `build/intermediate.txt`: Three-address code representation
- `build/output.asm`: x86 assembly code
- `compiler.log`: Compilation process logs

## Error Handling

The compiler provides detailed error messages for:
- Syntax errors (unexpected tokens, malformed expressions)
- Type errors (incompatible types in operations)
- Scope errors (undefined variables, duplicate declarations)
- Runtime configuration issues

## Development

To run tests:
```bash
pytest tests/
```

To check types:
```bash
mypy compiler/
```

To format code:
```bash
black compiler/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 