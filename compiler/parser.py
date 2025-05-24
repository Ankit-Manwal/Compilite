"""
This module implements a recursive descent parser for the compiler.
It constructs an Abstract Syntax Tree (AST) from a sequence of tokens,
implementing the following grammar features:
- Function and variable declarations
- Control flow statements (if, while)
- Expressions (arithmetic, logical, assignment)
- Type checking and scope management
"""

from .lexer import Token

class Parser:
    """
    A recursive descent parser that builds an AST from a token stream.
    Implements operator precedence and handles nested structures.
    
    The parser follows this precedence hierarchy (highest to lowest):
    1. Primary expressions (literals, identifiers, parenthesized)
    2. Unary operators (!, -)
    3. Multiplicative operators (*, /, %)
    4. Additive operators (+, -)
    5. Relational operators (<, >, <=, >=)
    6. Equality operators (==, !=)
    7. Logical AND (&&)
    8. Logical OR (||)
    9. Assignment (=)
    """
    
    def __init__(self, tokens):
        """
        Initialize the parser with a token stream.
        
        Args:
            tokens: List of Token objects from the lexer
            
        Filters out whitespace and comments, which aren't needed for parsing.
        """
        # Filter out whitespace and comments
        self.tokens = [t for t in tokens if t.type not in ['WHITESPACE', 'COMMENT']]
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
    
    def advance(self):
        """
        Move to the next token in the stream.
        Updates current_token to None if we reach the end.
        """
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def eat(self, token_type, value=None):
        """
        Consume a token if it matches the expected type and value.
        
        Args:
            token_type: Expected token type
            value: Optional specific value to match
            
        Raises:
            SyntaxError: If the current token doesn't match expectations
        """
        if not self.current_token:
            raise SyntaxError(f"Unexpected end of input, expected {token_type}")
        
        if self.current_token.type != token_type:
            expected = f"{token_type} '{value}'" if value else token_type
            got = f"{self.current_token.type}('{self.current_token.value}')"
            raise SyntaxError(f"Expected {expected}, got {got} at {self.current_token.line}:{self.current_token.column}")
        
        if value is not None and self.current_token.value != value:
            raise SyntaxError(f"Expected {token_type} '{value}', got '{self.current_token.value}' at {self.current_token.line}:{self.current_token.column}")
        
        self.advance()
    
    def parse(self):
        """
        Entry point for parsing. Returns the complete AST.
        
        Returns:
            list: List of top-level AST nodes (usually function/variable declarations)
        """
        return self.program()
    
    def program(self):
        """
        Parse the top level of the program.
        Handles function and variable declarations.
        
        Returns:
            list: List of declaration AST nodes
            
        Raises:
            SyntaxError: If an unexpected token is encountered
        """
        nodes = []
        while self.current_token:
            if self.current_token.type == 'KEYWORD' and self.current_token.value in ['int', 'float', 'char', 'void']:
                type_token = self.current_token
                self.eat('KEYWORD')
                
                if not self.current_token or self.current_token.type != 'IDENTIFIER':
                    raise SyntaxError("Expected identifier after type")
                
                if self.peek_next_token() and self.peek_next_token().value == '(':
                    nodes.append(self.function_declaration(type_token))
                else:
                    nodes.append(self.variable_declaration(type_token))
            else:
                raise SyntaxError(f"Unexpected token: {self.current_token}")
        return nodes
    
    def peek_next_token(self):
        """
        Look at the next token without consuming it.
        Used for lookahead in parsing decisions.
        
        Returns:
            Token: Next token or None if at end of stream
        """
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None
    
    def function_declaration(self, type_token):
        """
        Parse a function declaration including its parameter list and body.
        
        Args:
            type_token: Token containing the function's return type
            
        Returns:
            dict: AST node for the function declaration
        """
        func_name = self.current_token.value
        self.eat('IDENTIFIER')
        self.eat('SEPARATOR', '(')
        
        params = []
        if self.current_token.value != ')':
            params = self.parameters()
        self.eat('SEPARATOR', ')')
        
        body = self.block()
        return {
            'type': 'function_declaration',
            'return_type': type_token.value,
            'name': func_name,
            'parameters': params,
            'body': body
        }
    
    def parameters(self):
        """
        Parse function parameters.
        Handles multiple parameters separated by commas.
        
        Returns:
            list: List of parameter AST nodes
        """
        params = []
        while self.current_token and self.current_token.value != ')':
            param_type = self.current_token.value
            self.eat('KEYWORD')
            param_name = self.current_token.value
            self.eat('IDENTIFIER')
            params.append({'type': param_type, 'name': param_name})
            if self.current_token and self.current_token.value == ',':
                self.eat('SEPARATOR')
        return params
    
    def block(self):
        """
        Parse a block of statements enclosed in curly braces.
        
        Returns:
            list: List of statement AST nodes
        """
        self.eat('SEPARATOR', '{')
        statements = []
        while self.current_token and self.current_token.value != '}':
            statements.append(self.statement())
        self.eat('SEPARATOR', '}')
        return statements
    
    def statement(self):
        """
        Parse a single statement.
        Dispatches to specific statement parsers based on the current token.
        
        Returns:
            dict: AST node for the statement
        """
        print(f"DEBUG - Parsing statement, current token: {self.current_token}")  # Debug output
        if self.current_token.type == 'KEYWORD':
            if self.current_token.value in ['int', 'float', 'char']:
                return self.variable_declaration()
            elif self.current_token.value == 'return':
                return self.return_statement()
            elif self.current_token.value == 'while':
                return self.while_statement()
            elif self.current_token.value == 'if':
                return self.if_statement()
            elif self.current_token.value == 'print':
                return self.print_statement()
        return self.expression_statement()
    
    def print_statement(self):
        """
        Parse a print statement.
        Format: print(expression);
        
        Returns:
            dict: AST node for the print statement
        """
        print("DEBUG - Parsing print statement")  # Debug output
        self.eat('KEYWORD', 'print')
        self.eat('SEPARATOR', '(')
        expr = self.expression()
        print(f"DEBUG - Print expression: {expr}")  # Debug output
        self.eat('SEPARATOR', ')')
        self.eat('SEPARATOR', ';')
        return {
            'type': 'print_statement',
            'expression': expr
        }
    
    def while_statement(self):
        """
        Parse a while statement.
        Format: while (condition) { body }
        
        Returns:
            dict: AST node for the while statement
        """
        self.eat('KEYWORD', 'while')
        self.eat('SEPARATOR', '(')
        condition = self.expression()
        self.eat('SEPARATOR', ')')
        body = self.block()
        return {
            'type': 'while_statement',
            'condition': condition,
            'body': body
        }
    
    def if_statement(self):
        """
        Parse an if statement with optional else clause.
        Format: if (condition) { consequent } else { alternate }
        
        Returns:
            dict: AST node for the if statement
        """
        self.eat('KEYWORD', 'if')
        self.eat('SEPARATOR', '(')
        condition = self.expression()
        self.eat('SEPARATOR', ')')
        consequent = self.block()
        
        alternate = None
        if self.current_token and self.current_token.value == 'else':
            self.eat('KEYWORD', 'else')
            alternate = self.block()
        
        return {
            'type': 'if_statement',
            'condition': condition,
            'consequent': consequent,
            'alternate': alternate
        }
    
    def variable_declaration(self, type_token=None):
        """
        Parse a variable declaration with optional initialization.
        Format: type identifier [= expression];
        
        Args:
            type_token: Optional pre-read type token
            
        Returns:
            dict: AST node for the variable declaration
        """
        if not type_token:
            type_token = self.current_token
            self.eat('KEYWORD')
        
        name = self.current_token.value
        self.eat('IDENTIFIER')
        
        initializer = None
        if self.current_token and self.current_token.value == '=':
            self.eat('OPERATOR')
            initializer = self.expression()
        
        self.eat('SEPARATOR', ';')
        return {
            'type': 'variable_declaration',
            'var_type': type_token.value,
            'name': name,
            'initializer': initializer
        }
    
    def return_statement(self):
        """
        Parse a return statement.
        Format: return expression;
        
        Returns:
            dict: AST node for the return statement
        """
        self.eat('KEYWORD', 'return')
        expr = self.expression()
        self.eat('SEPARATOR', ';')
        return {
            'type': 'return_statement',
            'expression': expr
        }
    
    def expression_statement(self):
        """
        Parse an expression statement (expression followed by semicolon).
        Format: expression;
        
        Returns:
            dict: AST node for the expression statement
        """
        expr = self.expression()
        self.eat('SEPARATOR', ';')
        return {
            'type': 'expression_statement',
            'expression': expr
        }
    
    def expression(self):
        """
        Parse an expression.
        Currently just forwards to assignment_expression as the highest precedence.
        
        Returns:
            dict: AST node for the expression
        """
        return self.assignment_expression()
    
    def assignment_expression(self):
        """
        Parse an assignment expression.
        Format: identifier = expression
        
        Returns:
            dict: AST node for the assignment or higher precedence expression
        """
        left = self.logical_or_expression()
        
        if self.current_token and self.current_token.value == '=':
            self.eat('OPERATOR')
            right = self.assignment_expression()
            if isinstance(left, dict) and left['type'] == 'identifier':
                return {
                    'type': 'assignment_expression',
                    'left': left,
                    'right': right
                }
        return left
    
    def logical_or_expression(self):
        """
        Parse logical OR expressions.
        Format: logical_and_expression || logical_and_expression
        
        Returns:
            dict: AST node for the expression
        """
        left = self.logical_and_expression()
        
        while self.current_token and self.current_token.value == '||':
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.logical_and_expression()
            left = {
                'type': 'binary_expression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left
    
    def logical_and_expression(self):
        """
        Parse logical AND expressions.
        Format: equality_expression && equality_expression
        
        Returns:
            dict: AST node for the expression
        """
        left = self.equality_expression()
        
        while self.current_token and self.current_token.value == '&&':
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.equality_expression()
            left = {
                'type': 'binary_expression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left
    
    def equality_expression(self):
        """
        Parse equality expressions.
        Format: relational_expression (== | !=) relational_expression
        
        Returns:
            dict: AST node for the expression
        """
        left = self.relational_expression()
        
        while self.current_token and self.current_token.value in ['==', '!=']:
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.relational_expression()
            left = {
                'type': 'binary_expression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left
    
    def relational_expression(self):
        left = self.additive_expression()
        
        while self.current_token and self.current_token.value in ['<', '>', '<=', '>=']:
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.additive_expression()
            left = {
                'type': 'binary_expression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left
    
    def additive_expression(self):
        left = self.multiplicative_expression()
        
        while self.current_token and self.current_token.value in ['+', '-']:
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.multiplicative_expression()
            left = {
                'type': 'binary_expression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left
    
    def multiplicative_expression(self):
        left = self.unary_expression()
        
        while self.current_token and self.current_token.value in ['*', '/', '%']:
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.unary_expression()
            left = {
                'type': 'binary_expression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left
    
    def unary_expression(self):
        if self.current_token and self.current_token.value in ['+', '-', '!']:
            operator = self.current_token.value
            self.eat('OPERATOR')
            operand = self.unary_expression()
            return {
                'type': 'unary_expression',
                'operator': operator,
                'operand': operand
            }
        return self.primary_expression()
    
    def primary_expression(self):
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.advance()
            return {
                'type': 'number_literal',
                'value': token.value
            }
        elif token.type == 'STRING':
            self.advance()
            return {
                'type': 'string_literal',
                'value': token.value
            }
        elif token.type == 'IDENTIFIER':
            self.advance()
            return {
                'type': 'identifier',
                'name': token.value
            }
        elif token.value == '(':
            self.eat('SEPARATOR', '(')
            expr = self.expression()
            self.eat('SEPARATOR', ')')
            return expr
        else:
            raise SyntaxError(f"Unexpected token in primary expression: {token}")