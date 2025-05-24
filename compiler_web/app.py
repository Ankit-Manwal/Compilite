from flask import Flask, render_template, request, jsonify
import logging
import sys
import os

# Add parent directory to path so we can import the compiler module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.code_generator import IntermediateCodeGenerator, TargetCodeGenerator

app = Flask(__name__)

# Set up logging
log_file = 'debug.log'
try:
    # Try to create or open the log file
    with open(log_file, 'a') as f:
        pass
    
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
except Exception as e:
    print(f"Error setting up logging: {e}")
    # Fallback to just console logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s - %(message)s',
        force=True
    )

def log_debug(message):
    """Helper function to log debug messages"""
    logging.debug(str(message))  # Convert message to string to handle non-string objects

def ast_to_json(ast):
    """Convert AST to a JSON format suitable for visualization"""
    if isinstance(ast, list):
        return [ast_to_json(node) for node in ast]
    
    if not isinstance(ast, dict):
        return {"id": str(ast), "label": str(ast), "type": "literal"}
    
    node_id = f"{ast['type']}_{id(ast)}"
    node = {
        "id": node_id,
        "label": ast['type'],
        "type": ast['type'],
        "children": []
    }
    
    # Special handling for different node types
    if ast['type'] == 'function_declaration':
        node['label'] = f"Function: {ast.get('name', 'main')}"
    elif ast['type'] == 'variable_declaration':
        node['label'] = f"Var: {ast.get('name', '')}"
    elif ast['type'] == 'binary_expression':
        node['label'] = f"Op: {ast.get('operator', '')}"
    elif ast['type'] == 'number_literal':
        node['label'] = f"Number: {ast.get('value', '')}"
    elif ast['type'] == 'string_literal':
        value = ast.get('value', '')
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        node['label'] = f"String: {value}"
    elif ast['type'] == 'identifier':
        node['label'] = f"Id: {ast.get('name', '')}"
    elif ast['type'] == 'assignment_expression':
        if isinstance(ast['left'], dict) and ast['left']['type'] == 'identifier':
            node['label'] = f"Assign: {ast['left'].get('name', '')}"
    
    for key, value in ast.items():
        if key in ['type', 'name']:
            continue
        
        if isinstance(value, (dict, list)):
            children = ast_to_json(value)
            if isinstance(children, list):
                node['children'].extend(children)
            else:
                node['children'].append(children)
        else:
            child_id = f"{node_id}_{key}"
            child = {
                "id": child_id,
                "label": f"{key}: {value}",
                "type": "attribute"
            }
            node['children'].append(child)
    
    return node

def ast_to_tree(ast, indent=0):
    """Convert AST to a simple tree string representation"""
    if not ast:
        return ""
    
    if isinstance(ast, list):
        return "\n".join(ast_to_tree(node, indent) for node in ast if node)
    
    if not isinstance(ast, dict):
        return "  " * indent + str(ast)
    
    result = []
    node_type = ast.get('type', 'unknown')
    
    # Create the node representation
    node_str = "  " * indent + node_type
    
    # Add important attributes based on node type
    if node_type == 'function_declaration':
        node_str += f" ({ast.get('name', 'main')})"
    elif node_type == 'variable_declaration':
        node_str += f" ({ast.get('name', '')})"
    elif node_type == 'binary_expression':
        node_str += f" ({ast.get('operator', '')})"
    elif node_type == 'number_literal':
        node_str += f" ({ast.get('value', '')})"
    elif node_type == 'string_literal':
        value = ast.get('value', '')
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        node_str += f" ({value})"
    elif node_type == 'identifier':
        node_str += f" ({ast.get('name', '')})"
    
    result.append(node_str)
    
    # Process child nodes
    for key, value in ast.items():
        if key in ['type', 'name', 'value', 'operator']:
            continue
        
        if isinstance(value, (dict, list)):
            child_str = ast_to_tree(value, indent + 1)
            if child_str:
                result.append(child_str)
    
    return "\n".join(result)

def simulate_execution(ast):
    """Simulate the execution of the C code and return output"""
    output = []
    variables = {}
    MAX_ITERATIONS = 1000  # Add maximum iteration limit
    
    # Open output file
    with open('output.txt', 'w') as f:
        f.write("=== Program Execution Output ===\n\n")
    
    def write_output(msg):
        with open('output.txt', 'a') as f:
            f.write(str(msg) + '\n')
        log_debug(msg)
    
    def evaluate_expr(node):
        write_output(f"\nDEBUG - Evaluating expression: {node}")
        if not isinstance(node, dict):
            return node
        
        try:
            if node['type'] == 'number_literal':
                value = int(node['value'])
                write_output(f"DEBUG - Number literal value: {value}")
                return value
            elif node['type'] == 'identifier':
                var_name = node.get('name', '')
                if var_name not in variables:
                    raise NameError(f"Variable '{var_name}' is not defined")
                value = variables[var_name]
                write_output(f"DEBUG - Identifier '{var_name}' value: {value}")
                return value
            elif node['type'] == 'binary_expression':
                left = evaluate_expr(node['left'])
                right = evaluate_expr(node['right'])
                op = node['operator']
                result = None
                if op == '+': result = left + right
                elif op == '-': result = left - right
                elif op == '*': result = left * right
                elif op == '/': result = left // right if right != 0 else float('inf')
                elif op == '>': result = left > right
                elif op == '<': result = left < right
                elif op == '>=': result = left >= right
                elif op == '<=': result = left <= right
                elif op == '==': result = left == right
                write_output(f"DEBUG - Binary operation: {left} {op} {right} = {result}")
                return result
            elif node['type'] == 'string_literal':
                value = node['value']
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                write_output(f"DEBUG - String literal value: {value}")
                return value
            return 0
        except Exception as e:
            write_output(f"DEBUG - Error evaluating expression: {node}")
            write_output(f"DEBUG - Error: {str(e)}")
            raise
    
    def execute_node(node):
        write_output(f"\nDEBUG - Executing node: {node}")
        try:
            if not isinstance(node, dict):
                if isinstance(node, list):
                    for stmt in node:
                        execute_node(stmt)
                return
            
            if node['type'] == 'function_declaration':
                write_output("DEBUG - Executing function declaration")
                if 'body' in node:
                    for stmt in node['body']:
                        execute_node(stmt)
            
            elif node['type'] == 'variable_declaration':
                var_name = node.get('name', '')
                if var_name in variables:
                    raise NameError(f"Variable '{var_name}' is already defined")
                value = evaluate_expr(node['initializer']) if 'initializer' in node else 0
                variables[var_name] = value
                write_output(f"DEBUG - Declared variable {var_name} = {value}")
            
            elif node['type'] == 'assignment_expression':
                var_name = node['left'].get('name', '')
                if var_name not in variables:
                    raise NameError(f"Variable '{var_name}' is not defined")
                value = evaluate_expr(node['right'])
                variables[var_name] = value  # Update the variable value
                write_output(f"DEBUG - Assigned {var_name} = {value}")
            
            elif node['type'] == 'print_statement':
                write_output("\nDEBUG - Executing print statement")
                expr = node.get('expression', {})
                write_output(f"DEBUG - Print expression: {expr}")
                
                try:
                    if isinstance(expr, dict):
                        if expr['type'] == 'string_literal':
                            value = expr['value']
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                        else:
                            value = str(evaluate_expr(expr))
                    else:
                        value = str(expr)
                    
                    write_output(f"DEBUG - Print statement value: {value}")
                    output.append(value)
                    write_output(f"DEBUG - Current output buffer: {output}")
                except Exception as e:
                    write_output(f"DEBUG - Error in print statement: {str(e)}")
                    output.append(f"Error: {str(e)}")
            
            elif node['type'] == 'if_statement':
                condition = evaluate_expr(node['condition'])
                write_output(f"DEBUG - If condition result: {condition}")
                if condition:
                    write_output("DEBUG - Executing if branch")
                    if isinstance(node['consequent'], list):
                        for stmt in node['consequent']:
                            execute_node(stmt)
                    else:
                        execute_node(node['consequent'])
                elif node.get('alternate'):
                    write_output("DEBUG - Executing else branch")
                    if isinstance(node['alternate'], list):
                        for stmt in node['alternate']:
                            execute_node(stmt)
                    else:
                        execute_node(node['alternate'])
            
            elif node['type'] == 'while_statement':
                iterations = 0
                write_output("DEBUG - Starting while loop")
                while evaluate_expr(node['condition']):
                    iterations += 1
                    if iterations > MAX_ITERATIONS:
                        raise RuntimeError(f"Maximum iteration limit ({MAX_ITERATIONS}) exceeded in while loop")
                    write_output(f"DEBUG - While loop iteration {iterations}")
                    if isinstance(node['body'], list):
                        for stmt in node['body']:
                            execute_node(stmt)
                    else:
                        execute_node(node['body'])
                    write_output(f"DEBUG - After iteration {iterations}, variables: {variables}")
            
            elif node['type'] == 'block_statement' and 'body' in node:
                write_output("DEBUG - Executing block statement")
                for stmt in node['body']:
                    execute_node(stmt)
            
            elif node['type'] == 'expression_statement':
                write_output("DEBUG - Executing expression statement")
                execute_node(node['expression'])
            
            write_output(f"DEBUG - Current variables: {variables}")
            
        except Exception as e:
            write_output(f"DEBUG - Error executing node: {node}")
            write_output(f"DEBUG - Error: {str(e)}")
            raise
    
    try:
        write_output("\nDEBUG - Starting program simulation")
        if isinstance(ast, list):
            for node in ast:
                execute_node(node)
        else:
            execute_node(ast)
        write_output(f"\nDEBUG - Final variables: {variables}")
        write_output(f"DEBUG - Final output: {output}")
        
        # Ensure output is not empty
        if not output:
            write_output("DEBUG - No output generated during execution")
            output.append("(No output generated)")
            
        # Write final program output
        with open('output.txt', 'a') as f:
            f.write("\n=== Program Output ===\n")
            for line in output:
                f.write(line + '\n')
            
    except Exception as e:
        write_output(f"\nDEBUG - Runtime error: {str(e)}")
        output.append(f"Runtime Error: {str(e)}")
    
    return output

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    """Compile the code and return all stages"""
    try:
        source_code = request.json['code']
        log_debug("\nDEBUG - Received source code:")
        log_debug(source_code)
        
        # Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        token_list = [{'type': token.type, 'value': token.value} for token in tokens]
        log_debug("\nDEBUG - Tokens:")
        log_debug(str(token_list))
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Debug print AST
        log_debug("\nDEBUG - Full AST:")
        import json
        log_debug(json.dumps(ast, indent=2))
        
        # Get the main function (first function declaration)
        if isinstance(ast, list) and len(ast) > 0:
            main_func = ast[0]
        else:
            main_func = ast
            
        log_debug("\nDEBUG - Main function:")
        log_debug(json.dumps(main_func, indent=2))
        
        # Create simple tree representation
        ast_tree = ast_to_tree(main_func)
        log_debug("\nAST Tree Structure:")
        log_debug(ast_tree)
        
        # Generate intermediate code
        ir_generator = IntermediateCodeGenerator(main_func)
        ir_code = ir_generator.generate()
        log_debug("\nDEBUG - Intermediate Code:")
        log_debug(str(ir_code))
        
        # Generate target code
        target_generator = TargetCodeGenerator(ir_code)
        target_code = target_generator.generate()
        log_debug("\nDEBUG - Target Code:")
        log_debug(str(target_code))
        
        # Simulate execution with debug output
        log_debug("\nDEBUG - Starting program execution:")
        output = simulate_execution(main_func)
        log_debug("\nDEBUG - Program output:")
        log_debug(str(output))
        
        return jsonify({
            'success': True,
            'tokens': token_list,
            'ast': ast_tree,
            'ir_code': ir_code,
            'target_code': target_code,
            'output': output
        })
        
    except Exception as e:
        import traceback
        log_debug("\nDEBUG - Error:" + str(e))
        log_debug("DEBUG - Traceback:" + traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/example')
def get_example():
    """Return an example C code"""
    example_code = """int main() {
    // Initialize variables
    int x = 5;
    int y = 10;
    
    // Test arithmetic
    int z = x + y * 2;
    
    // Test if-else
    if (z > 20) {
        print("z is greater than 20");
        x = x + 1;
    } else {
        print("z is 20 or less");
        y = y - 1;
    }
    
    // Test while loop
    while (x < y) {
        x = x + 1;
        print(x);
    }
    
    return 0;
}"""
    return jsonify({'code': example_code})

if __name__ == '__main__':
    app.run(debug=True) 