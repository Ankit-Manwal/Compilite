"""
This module implements the lexical analyzer (lexer) for the compiler.
It breaks down source code into a sequence of tokens, handling:
- Keywords and identifiers
- Numbers and string literals
- Operators and separators
- Comments and whitespace
- Line and column tracking for error reporting
"""

import re

class Token:
    """
    Represents a token in the source code with its type, value, and position.
    
    Attributes:
        type: Token type (e.g., 'KEYWORD', 'IDENTIFIER', etc.)
        value: Actual text of the token
        line: Line number where token appears (1-based)
        column: Column number where token starts (1-based)
    """
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        """Returns a string representation of the token for debugging"""
        return f"{self.type}({self.value}) at {self.line}:{self.column}"


class Lexer:
    """
    Breaks down source code into a sequence of tokens using regular expressions.
    Handles complex features like comments, string literals, and precise error locations.
    
    The lexer uses a single master regex pattern compiled from individual token patterns,
    which is more efficient than checking each pattern separately.
    """
    
    # Token specifications as (name, regex_pattern) pairs
    # Order matters! Earlier patterns take precedence
    TOKEN_SPEC = [
        ('WHITESPACE', r'[ \t\r\n]+'),  # Spaces, tabs, carriage returns, newlines
        
        ('COMMENT', r'//[^\n]*|/\*(?:[^*]|\*[^/])*\*/'),  # Single and multi-line comments
        ('KEYWORD', r'\b(int|float|char|if|else|while|for|return|void|print)\b'),  # Language keywords
        ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),  # String literals with escape sequence support
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Variable and function names
        ('NUMBER', r'\d+(\.\d+)?'),  # Integer and floating-point numbers
        ('OPERATOR', r'==|!=|<=|>=|[+\-*/%=<>!]'),  # Arithmetic and comparison operators
        ('SEPARATOR', r'[(),;{}]'),  # Punctuation and grouping symbols
        ('UNKNOWN', r'.')  # Catch-all for invalid characters
    ]

    def __init__(self, code):
        """
        Initialize the lexer with source code.
        
        Args:
            code: Source code string to tokenize
            
        The lexer maintains state about the current position in the source code
        to provide accurate line and column numbers for error reporting.
        """
        self.code = code
        self.line = 1  # Current line number (1-based)
        self.column = 1  # Current column number (1-based)
        self.pos = 0  # Current position in source code
        self.tokens = []  # List of generated tokens

        # Compile all token patterns into a single master pattern
        regex_parts = []
        for name, pattern in self.TOKEN_SPEC:
            regex_parts.append(f'(?P<{name}>{pattern})')
        self.master_pattern = re.compile('|'.join(regex_parts))

    def tokenize(self):
        """
        Convert the source code into a list of tokens.
        
        Returns:
            list: List of Token objects
            
        Raises:
            SyntaxError: If an illegal character is encountered
            
        The tokenizer:
        1. Uses regex to find the next token
        2. Updates line/column numbers
        3. Handles special cases (comments, strings)
        4. Creates Token objects
        """
        for match in self.master_pattern.finditer(self.code):
            kind = match.lastgroup  # Token type from regex group name
            value = match.group()  # Actual text that matched
            # Calculate column based on last newline
            column = match.start() - self.code.rfind('\n', 0, match.start())

            # Skip whitespace but update line/column numbers
            if kind == 'WHITESPACE':
                if '\n' in value:
                    self.line += value.count('\n')
                    self.column = len(value.split('\n')[-1]) + 1
                else:
                    self.column += len(value)
                continue

            # Skip comments but update line/column numbers
            if kind == 'COMMENT':
                if '\n' in value:
                    self.line += value.count('\n')
                    self.column = len(value.split('\n')[-1]) + 1
                else:
                    self.column += len(value)
                continue

            # Report illegal characters with location
            if kind == 'UNKNOWN':
                raise SyntaxError(f"Illegal character '{value}' at line {self.line}, column {self.column}")

            # Handle string literals - process escape sequences
            if kind == 'STRING':
                value = value.encode('utf-8').decode('unicode_escape')
                print(f"DEBUG - String literal found: {value}")

            # Special debug output for print statements
            if kind == 'KEYWORD' and value == 'print':
                print(f"DEBUG - Print keyword found at line {self.line}, column {self.column}")

            # Create and store the token
            token = Token(kind, value, self.line, self.column)
            print(f"DEBUG - Created token: {token}")  # Debug output
            self.tokens.append(token)

            # Update line and column numbers
            if '\n' in value:
                self.line += value.count('\n')
                self.column = len(value.split('\n')[-1]) + 1
            else:
                self.column += len(value)

        return self.tokens
