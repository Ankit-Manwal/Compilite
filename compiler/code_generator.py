"""
This module contains two main classes for code generation:
1. IntermediateCodeGenerator: Generates three-address code (TAC) from the AST
2. TargetCodeGenerator: Converts TAC to x86 assembly code
"""

class IntermediateCodeGenerator:
    """
    Generates three-address code (TAC) from an Abstract Syntax Tree (AST).
    TAC is an intermediate representation where each instruction has at most
    three operands (e.g., x = y + z).
    
    Attributes:
        ast: The root node of the Abstract Syntax Tree
        instructions: List of generated TAC instructions
        temp_counter: Counter for generating unique temporary variables
        label_counter: Counter for generating unique labels
    """
    
    def __init__(self, ast):
        self.ast = ast
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def generate(self):
        """
        Entry point for code generation. Processes the AST and returns
        the list of generated TAC instructions.
        
        Returns:
            list: Generated TAC instructions
        """
        if isinstance(self.ast, list):
            for node in self.ast:
                self.visit(node)
        else:
            self.visit(self.ast)
        return self.instructions
    
    def new_temp(self):
        """
        Generates a new unique temporary variable name.
        
        Returns:
            str: Name of the new temporary variable (e.g., 't0', 't1', etc.)
        """
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self):
        """
        Generates a new unique label for control flow.
        
        Returns:
            str: Name of the new label (e.g., 'L0', 'L1', etc.)
        """
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def visit(self, node):
        """
        Generic visitor that dispatches to the appropriate visit method
        based on the node type.
        
        Args:
            node: AST node to visit
            
        Returns:
            str: Result of the visit (usually a temporary variable name)
        """
        if not isinstance(node, dict):
            return str(node)
        
        method_name = f'visit_{node["type"]}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """
        Called when no specific visit method exists for a node type.
        Raises an exception with helpful debugging information.
        
        Args:
            node: AST node that couldn't be visited
            
        Raises:
            Exception: With list of available visitor methods
        """
        available_methods = [method for method in dir(self) if method.startswith('visit_')]
        raise Exception(f"No visit method for {node['type']}. Available visitors: {', '.join(available_methods)}")
    
    def visit_function_declaration(self, node):
        """
        Generates TAC for function declarations. Handles function parameters
        and ensures main function has a return statement.
        
        Args:
            node: Function declaration AST node
        """
        self.instructions.append(f"FUNCTION {node.get('name', 'main')}:")
        
        if 'parameters' in node:
            for param in node['parameters']:
                self.instructions.append(f"PARAM {param['name']}")
        
        if 'body' in node:
            for stmt in node['body']:
                self.visit(stmt)
        
        if node.get('name', 'main') == 'main' and not any(instr.startswith('RETURN') for instr in self.instructions):
            self.instructions.append("RETURN 0")
    
    def visit_variable_declaration(self, node):
        if 'initializer' in node and node['initializer']:
            temp = self.visit(node['initializer'])
            self.instructions.append(f"STORE {temp}, {node['name']}")
        else:
            self.instructions.append(f"DECLARE {node['name']}")
    
    def visit_while_statement(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.instructions.append(f"LABEL {start_label}")
        condition_temp = self.visit(node['condition'])
        self.instructions.append(f"IF_FALSE {condition_temp} GOTO {end_label}")
        
        if isinstance(node['body'], list):
            for stmt in node['body']:
                self.visit(stmt)
        else:
            self.visit(node['body'])
        
        self.instructions.append(f"GOTO {start_label}")
        self.instructions.append(f"LABEL {end_label}")
    
    def visit_if_statement(self, node):
        condition_temp = self.visit(node['condition'])
        false_label = self.new_label()
        end_label = self.new_label()
        
        self.instructions.append(f"IF_FALSE {condition_temp} GOTO {false_label}")
        
        if isinstance(node['consequent'], list):
            for stmt in node['consequent']:
                self.visit(stmt)
        else:
            self.visit(node['consequent'])
        
        if node.get('alternate'):
            self.instructions.append(f"GOTO {end_label}")
            self.instructions.append(f"LABEL {false_label}")
            
            if isinstance(node['alternate'], list):
                for stmt in node['alternate']:
                    self.visit(stmt)
            else:
                self.visit(node['alternate'])
                
            self.instructions.append(f"LABEL {end_label}")
        else:
            self.instructions.append(f"LABEL {false_label}")
    
    def visit_print_statement(self, node):
        expr_temp = self.visit(node['expression'])
        self.instructions.append(f"PRINT {expr_temp}")
    
    def visit_binary_expression(self, node):
        left_temp = self.visit(node['left'])
        right_temp = self.visit(node['right'])
        result_temp = self.new_temp()
        
        op_map = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD',
            '==': 'EQ', '!=': 'NE', '<': 'LT', '<=': 'LE', '>': 'GT', '>=': 'GE',
            '&&': 'AND', '||': 'OR'
        }
        
        self.instructions.append(f"{result_temp} = {left_temp} {op_map[node['operator']]} {right_temp}")
        return result_temp
    
    def visit_unary_expression(self, node):
        operand_temp = self.visit(node['operand'])
        result_temp = self.new_temp()
        
        if node['operator'] == '-':
            self.instructions.append(f"{result_temp} = NEG {operand_temp}")
        elif node['operator'] == '!':
            self.instructions.append(f"{result_temp} = NOT {operand_temp}")
        else:
            self.instructions.append(f"{result_temp} = {operand_temp}")
        
        return result_temp
    
    def visit_assignment_expression(self, node):
        right_temp = self.visit(node['right'])
        left_name = node['left']['name']
        self.instructions.append(f"STORE {right_temp}, {left_name}")
        return right_temp
    
    def visit_return_statement(self, node):
        if node.get('expression'):
            temp = self.visit(node['expression'])
            self.instructions.append(f"RETURN {temp}")
        else:
            self.instructions.append("RETURN")
    
    def visit_identifier(self, node):
        temp = self.new_temp()
        self.instructions.append(f"{temp} = LOAD {node['name']}")
        return temp
    
    def visit_number_literal(self, node):
        temp = self.new_temp()
        self.instructions.append(f"{temp} = {node['value']}")
        return temp
    
    def visit_string_literal(self, node):
        temp = self.new_temp()
        self.instructions.append(f"{temp} = \"{node['value']}\"")
        return temp
    
    def visit_expression_statement(self, node):
        return self.visit(node['expression'])





class TargetCodeGenerator:
    """
    Converts three-address code (TAC) to x86 assembly code.
    Handles register allocation, memory management, and system calls.
    
    Attributes:
        intermediate_code: List of TAC instructions to convert
        target_code: Generated assembly instructions
        string_counter: Counter for unique string labels
        label_counter: Counter for unique assembly labels
        variables: Set of program variables that need memory allocation
        strings: Dictionary mapping string literals to their labels
    """
    
    def __init__(self, intermediate_code):
        self.intermediate_code = intermediate_code
        self.target_code = []
        self.string_counter = 0
        self.label_counter = 0
        self.variables = set()
        self.strings = {}
    
    def generate(self):
        """
        Main method to generate x86 assembly code from TAC.
        Handles data section (variables and strings) and text section (code).
        
        Returns:
            list: Generated assembly instructions
        """
        # Data section for global variables and constants
        self.target_code.append("section .data")
        self.target_code.append("    fmt_int db '%d', 10, 0")  # Format string for printing integers
        self.target_code.append("    fmt_str db '%s', 10, 0")  # Format string for printing strings
        
        # First pass: collect all variables and string literals
        self._collect_symbols()
        
        # Declare space for variables
        for var in self.variables:
            self.target_code.append(f"    {var} dd 0")  # 32-bit integer variables
        
        # Declare string literals
        for str_val, label in self.strings.items():
            self.target_code.append(f"    {label} db {str_val}, 0")
        
        # Text section for code
        self.target_code.append("\nsection .text")
        self.target_code.append("    global main")
        self.target_code.append("    extern printf")  # External C function for printing
        
        # Convert each TAC instruction to assembly
        current_function = None
        for instr in self.intermediate_code:
            if instr.startswith("FUNCTION"):
                current_function = instr.split()[1].rstrip(":")
                self.target_code.append(f"\n{current_function}:")
                
                if current_function == "main":
                    # Set up stack frame for main function
                    self.target_code.append("    push ebp")
                    self.target_code.append("    mov ebp, esp")
            else:
                asm_code = self._convert_instruction(instr)
                if isinstance(asm_code, list):
                    self.target_code.extend(["    " + line for line in asm_code])
                elif asm_code:
                    self.target_code.append("    " + asm_code)
        
        return self.target_code
    
    def _collect_symbols(self):
        for instr in self.intermediate_code:
            parts = instr.split()
            if "STORE" in instr:
                var_name = parts[-1].rstrip(",")
                self.variables.add(var_name)
            elif "LOAD" in instr and not instr.startswith("t"):
                var_name = parts[1].rstrip(",")
                if not var_name.startswith("#"):
                    self.variables.add(var_name)
            elif '"' in instr:
                str_val = instr[instr.find('"'):instr.rfind('"')+1]
                if str_val not in self.strings:
                    label = f"str_{self.string_counter}"
                    self.strings[str_val] = label
                    self.string_counter += 1
    
    def _convert_instruction(self, instr):
        parts = instr.split()
        
        if "=" in instr:
            dest = parts[0]
            if "LOAD" in instr:
                var = parts[-1]
                return f"mov eax, [{var}]"
            elif parts[2] in ["ADD", "SUB", "MUL", "DIV"]:
                op1, op, op2 = parts[2:5]
                if op == "ADD":
                    return [
                        f"mov eax, {op1}",
                        f"add eax, {op2}"
                    ]
                elif op == "SUB":
                    return [
                        f"mov eax, {op1}",
                        f"sub eax, {op2}"
                    ]
                elif op == "MUL":
                    return [
                        f"mov eax, {op1}",
                        f"imul eax, {op2}"
                    ]
                elif op == "DIV":
                    return [
                        f"mov eax, {op1}",
                        f"cdq",
                        f"idiv {op2}"
                    ]
        elif instr.startswith("PRINT"):
            expr = parts[1]
            if expr.startswith('"'):
                str_label = self.strings[expr]
                return [
                    f"push {str_label}",
                    f"push fmt_str",
                    f"call printf",
                    f"add esp, 8"
                ]
            else:
                return [
                    f"push {expr}",
                    f"push fmt_int",
                    f"call printf",
                    f"add esp, 8"
                ]
        elif instr.startswith("STORE"):
            value, var = parts[1].rstrip(","), parts[2]
            return f"mov [{var}], {value}"
        elif instr.startswith("RETURN"):
            if len(parts) > 1:
                return [
                    f"mov eax, {parts[1]}",
                    "mov esp, ebp",
                    "pop ebp",
                    "ret"
                ]
            else:
                return [
                    "mov eax, 0",
                    "mov esp, ebp",
                    "pop ebp",
                    "ret"
                ]
        elif instr.startswith("LABEL"):
            return f"{parts[1].rstrip(':')}:"
        elif instr.startswith("GOTO"):
            return f"jmp {parts[1]}"
        elif instr.startswith("IF_FALSE"):
            return f"jz {parts[-1]}"
        
        return None