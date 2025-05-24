"""
This module implements a symbol table for tracking variables and their scopes.
The symbol table is a crucial component for:
- Managing variable declarations and scopes
- Type checking and validation
- Preventing duplicate variable declarations
- Ensuring variables are declared before use
"""

class SymbolTable:
    """
    A symbol table implementation that supports nested scopes.
    Uses a stack of dictionaries to represent scope hierarchy.
    
    Each symbol entry contains:
    - type: The data type of the symbol (int, float, char, etc.)
    - value: Optional initial value or additional metadata
    
    Attributes:
        symbols: Legacy dictionary (maintained for compatibility)
        scopes: Stack of scope dictionaries, innermost scope at top
    """
    
    def __init__(self):
        """
        Initialize an empty symbol table with a global scope.
        The scopes list acts as a stack with the global scope at the bottom.
        """
        self.symbols = {}  # Legacy, kept for backward compatibility
        self.scopes = [{}]  # Initialize with global scope
    
    def enter_scope(self):
        """
        Create a new scope by pushing an empty dictionary onto the scope stack.
        Called when entering a new block (function, if, while, etc.).
        """
        self.scopes.append({})
    
    def exit_scope(self):
        """
        Exit the current scope by popping it from the scope stack.
        Only pops if there's more than one scope (preserves global scope).
        """
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def add_symbol(self, name, symbol_type, value=None):
        """
        Add a new symbol to the current (innermost) scope.
        
        Args:
            name: Name of the symbol (variable/function name)
            symbol_type: Type of the symbol (int, float, function, etc.)
            value: Optional initial value or additional data
            
        Raises:
            NameError: If symbol already exists in current scope
        """
        if name in self.scopes[-1]:
            raise NameError(f"Symbol '{name}' already defined in current scope")
        self.scopes[-1][name] = {
            'type': symbol_type,
            'value': value
        }
    
    def lookup(self, name):
        """
        Look up a symbol in all scopes, from innermost to outermost.
        
        Args:
            name: Name of the symbol to look up
            
        Returns:
            dict: Symbol entry containing type and value
            
        Raises:
            NameError: If symbol is not found in any scope
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"Symbol '{name}' not found")
    
    def update_symbol(self, name, value):
        """
        Update the value of an existing symbol in the nearest enclosing scope.
        
        Args:
            name: Name of the symbol to update
            value: New value for the symbol
            
        Raises:
            NameError: If symbol is not found in any scope
        """
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['value'] = value
                return
        raise NameError(f"Symbol '{name}' not found")