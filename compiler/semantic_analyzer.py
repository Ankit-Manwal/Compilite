"""
This module implements semantic analysis for the compiler.
It performs type checking, scope analysis, and ensures program correctness
beyond syntax. The analyzer uses a symbol table to track variables and their types.
"""

from .symbol_table import SymbolTable

class SemanticAnalyzer:
    """Ī
    Performs semantic analysis on the AST to ensure program correctness.
    Implements type checking, scope analysis, and symbol table management.
    
    Attributes:
        ast: The Abstract Syntax Tree to analyze
        symbol_table: Tracks variables, functions, and their types across scopes
    """
    
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
    
    def analyze(self):
        """
        Entry point for semantic analysis. Processes each node in the AST.
        Raises TypeError for any semantic violations found.
        """
        for node in self.ast:
            self.visit(node)
    
    def visit(self, node):
        """
        Generic visitor that dispatches to the appropriate visit method
        based on the node type.
        
        Args:
            node: AST node to visit
            
        Returns:
            str: Type of the visited node
        """
        method_name = f'visit_{node["type"]}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """
        Called when no specific visit method exists for a node type.
        
        Args:
            node: AST node that couldn't be visited
            
        Raises:
            Exception: Always, as missing visitors indicate unhandled node types
        """
        raise Exception(f"No visit method for {node['type']}")
    
    def visit_function_declaration(self, node):
        """
        Analyzes function declarations. Creates a new scope for the function body
        and processes parameters and function body statements.
        
        Args:
            node: Function declaration AST node
            
        Side effects:
            - Adds function to symbol table
            - Creates new scope for function body
        """
        self.symbol_table.add_symbol(node['name'], 'function', node)
        self.symbol_table.enter_scope()
        
        for param in node['parameters']:
            self.symbol_table.add_symbol(param['name'], param['type'])
        
        for stmt in node['body']:
            self.visit(stmt)
        
        self.symbol_table.exit_scope()
    
    def visit_variable_declaration(self, node):
        """
        Analyzes variable declarations. Performs type checking if there's
        an initializer expression.
        
        Args:
            node: Variable declaration AST node
            
        Raises:
            TypeError: If initializer type doesn't match variable type
            
        Side effects:
            Adds variable to symbol table
        """
        if 'initializer' in node and node['initializer']:
            value_type = self.visit(node['initializer'])
            var_type = node['var_type']
            
            if var_type == 'int' and value_type not in ['int', 'float']:
                raise TypeError(f"Cannot assign {value_type} to int variable {node['name']}")
            elif var_type == 'float' and value_type not in ['int', 'float']:
                raise TypeError(f"Cannot assign {value_type} to float variable {node['name']}")
            elif var_type == 'char' and value_type != 'char':
                raise TypeError(f"Cannot assign {value_type} to char variable {node['name']}")
        
        self.symbol_table.add_symbol(node['name'], node['var_type'], node.get('initializer'))
    
    def visit_binary_expression(self, node):
        """
        Analyzes binary expressions. Ensures operand types are compatible
        with the operator and determines the result type.
        
        Args:
            node: Binary expression AST node
            
        Returns:
            str: Type of the expression result
            
        Raises:
            TypeError: If operand types are incompatible with the operator
        """
        left_type = self.visit(node['left'])
        right_type = self.visit(node['right'])
        
        if node['operator'] in ['+', '-', '*', '/', '%']:
            if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                raise TypeError(f"Cannot perform arithmetic on {left_type} and {right_type}")
            return left_type if left_type == right_type else 'float'
        elif node['operator'] in ['==', '!=', '<', '>', '<=', '>=']:
            if left_type != right_type:
                raise TypeError(f"Cannot compare {left_type} with {right_type}")
            return 'int'  # Comparison operators return boolean (represented as int)
        elif node['operator'] in ['&&', '||']:
            if left_type != 'int' or right_type != 'int':
                raise TypeError(f"Logical operators require 'int' operands")
            return 'int'  # Logical operators return boolean (represented as int)
        else:
            raise TypeError(f"Unknown operator {node['operator']}")
    
    def visit_unary_expression(self, node):
        """
        Analyzes unary expressions. Ensures operand type is compatible
        with the operator and determines the result type.
        
        Args:
            node: Unary expression AST node
            
        Returns:
            str: Type of the expression result
            
        Raises:
            TypeError: If operand type is incompatible with the operator
        """
        operand_type = self.visit(node['operand'])
        if node['operator'] in ['+', '-']:
            if operand_type not in ['int', 'float']:
                raise TypeError(f"Cannot apply unary {node['operator']} to {operand_type}")
            return operand_type
        elif node['operator'] == '!':
            if operand_type != 'int':
                raise TypeError(f"Cannot apply logical NOT to {operand_type}")
            return 'int'  # Logical NOT returns boolean (represented as int)
        else:
            raise TypeError(f"Unknown unary operator {node['operator']}")
    
    def visit_while_statement(self, node):
        """
        Analyzes while statements. Ensures condition is boolean (int)
        and creates a new scope for the loop body.
        
        Args:
            node: While statement AST node
            
        Raises:
            TypeError: If condition is not boolean (int)
            
        Side effects:
            Creates new scope for loop body
        """
        condition_type = self.visit(node['condition'])
        if condition_type != 'int':
            raise TypeError(f"While condition must be 'int', got '{condition_type}'")
        
        self.symbol_table.enter_scope()
        for stmt in node['body']:
            self.visit(stmt)
        self.symbol_table.exit_scope()
    
    def visit_if_statement(self, node):
        """
        Analyzes if statements. Ensures condition is boolean (int)
        and creates new scopes for both branches.
        
        Args:
            node: If statement AST node
            
        Raises:
            TypeError: If condition is not boolean (int)
            
        Side effects:
            Creates new scopes for both branches
        """
        condition_type = self.visit(node['condition'])
        if condition_type != 'int':
            raise TypeError(f"If condition must be 'int', got '{condition_type}'")
        
        self.symbol_table.enter_scope()
        for stmt in node['consequent']:
            self.visit(stmt)
        self.symbol_table.exit_scope()
        
        if node['alternate']:
            self.symbol_table.enter_scope()
            for stmt in node['alternate']:
                self.visit(stmt)
            self.symbol_table.exit_scope()
    
    def visit_print_statement(self, node):
        """
        Analyzes print statements. Returns the type of the expression
        being printed.
        
        Args:
            node: Print statement AST node
            
        Returns:
            str: Type of the expression being printed
        """
        return self.visit(node['expression'])
    
    def visit_return_statement(self, node):
        """
        Analyzes return statements. Returns the type of the returned
        expression or 'void' if no expression.
        
        Args:
            node: Return statement AST node
            
        Returns:
            str: Type of the returned expression or 'void'
        """
        if 'expression' in node and node['expression']:
            return self.visit(node['expression'])
        return 'void'
    
    def visit_identifier(self, node):
        """
        Analyzes identifiers. Looks up the identifier in the symbol table
        and returns its type.
        
        Args:
            node: Identifier AST node
            
        Returns:
            str: Type of the identifier
        """
        symbol = self.symbol_table.lookup(node['name'])
        return symbol['type']
    
    def visit_number_literal(self, node):
        """
        Analyzes number literals. Determines if the number is int or float.
        
        Args:
            node: Number literal AST node
            
        Returns:
            str: 'float' if number contains decimal point, 'int' otherwise
        """
        value = node['value']
        return 'float' if '.' in str(value) else 'int'
    
    def visit_string_literal(self, node):
        """
        Analyzes string literals. All string literals have type 'char*'.
        
        Args:
            node: String literal AST node
            
        Returns:
            str: Always returns 'char*'
        """
        return 'char*'
    
    def visit_assignment_expression(self, node):
        """
        Analyzes assignment expressions. Ensures left and right sides
        have compatible types.
        
        Args:
            node: Assignment expression AST node
            
        Returns:
            str: Type of the assignment (same as left side)
            
        Raises:
            TypeError: If types don't match
        """
        left_type = self.visit(node['left'])
        right_type = self.visit(node['right'])
        
        if left_type != right_type:
            raise TypeError(f"Type mismatch in assignment: {left_type} != {right_type}")
        
        return left_type

    def visit_expression_statement(self, node):
        """
        Analyzes expression statements. Returns the type of the expression.
        
        Args:
            node: Expression statement AST node
            
        Returns:
            str: Type of the contained expression
        """
        return self.visit(node['expression'])