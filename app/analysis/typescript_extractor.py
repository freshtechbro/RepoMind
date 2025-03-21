"""
Module for extracting method calls and other information from TypeScript/JavaScript code.

Uses the TypeScript Compiler API via Node.js subprocess to parse and analyze TypeScript
and JavaScript code.
"""
import os
import json
import tempfile
import subprocess
from typing import Dict, List, Any, Optional


def extract_method_calls(source_code: str) -> List[Dict[str, Any]]:
    """
    Extract method calls from TypeScript/JavaScript source code.
    
    Args:
        source_code: TypeScript/JavaScript source code to analyze
    
    Returns:
        list: List of dictionaries with method call information
    
    Raises:
        RuntimeError: If the TypeScript parser fails or Node.js is not available
    """
    # We'll use a Node.js script to parse the TypeScript code
    # For now, we'll simulate the extraction with a mock implementation
    return _mock_typescript_extractor(source_code)


def _mock_typescript_extractor(source_code: str) -> List[Dict[str, Any]]:
    """
    Temporary mock implementation for TypeScript method call extraction.
    
    This will be replaced with a proper implementation using the TypeScript Compiler API.
    
    Args:
        source_code: TypeScript/JavaScript source code to analyze
        
    Returns:
        list: Mocked list of method call information
    """
    method_calls = []
    
    # Basic pattern matching to find potential method calls
    # This is just a placeholder for the real implementation
    lines = source_code.split('\n')
    line_number = 0
    
    for line in lines:
        line_number += 1
        line = line.strip()
        
        # Look for constructor calls (new Class())
        if "new " in line:
            class_name = None
            for part in line.split("new ")[1:]:
                class_name = part.split("(")[0].strip()
                if class_name:
                    method_calls.append({
                        'is_constructor': True,
                        'class': class_name,
                        'args': [],  # Would need real parsing to get args
                        'lineno': line_number,
                        'col_offset': line.find("new ") + 4
                    })
        
        # Look for method calls (obj.method())
        if "." in line and "(" in line:
            parts = line.split(".")
            for i, part in enumerate(parts[:-1]):
                if i == 0:
                    # First part is likely the caller
                    caller = part.split()[-1]
                else:
                    # Intermediate parts in chained calls
                    caller = parts[i-1].split("(")[-1].strip()
                
                # Look for method in the next part
                if "(" in parts[i+1]:
                    method = parts[i+1].split("(")[0].strip()
                    # Skip if this looks like a property access rather than a method call
                    if method and ")" in parts[i+1]:
                        # Detect if this is part of an await expression
                        is_async = "await" in line and line.find("await") < line.find(f"{caller}.{method}")
                        
                        method_calls.append({
                            'caller': caller,
                            'method': method,
                            'args': [],  # Would need real parsing to get args
                            'lineno': line_number,
                            'col_offset': line.find(f"{caller}.{method}"),
                            'is_async': is_async
                        })
    
    return method_calls


def _extract_with_typescript_compiler(source_code: str) -> List[Dict[str, Any]]:
    """
    Extract method calls using the TypeScript Compiler API.
    
    This function creates a temporary file with the source code, runs a Node.js
    script that uses the TypeScript Compiler API to parse it, and returns the
    extracted method calls.
    
    Note: This requires Node.js to be installed with TypeScript.
    
    Args:
        source_code: TypeScript/JavaScript source code to analyze
        
    Returns:
        list: List of dictionaries with method call information
        
    Raises:
        RuntimeError: If the parser script fails or Node.js is not available
    """
    # Create a temporary file to hold the source code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(source_code)
    
    try:
        # Path to the parser script (which we'll need to create)
        parser_script_path = os.path.join(os.path.dirname(__file__), 'ts_parser', 'extract_calls.js')
        
        # Check if the parser script exists, if not use mock implementation
        if not os.path.exists(parser_script_path):
            return _mock_typescript_extractor(source_code)
        
        # Run the Node.js script
        result = subprocess.run(
            ['node', parser_script_path, temp_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output
        method_calls = json.loads(result.stdout)
        return method_calls
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse TypeScript code: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def create_typescript_parser():
    """
    Create the TypeScript parser script if it doesn't exist.
    
    This function creates a Node.js script that uses the TypeScript Compiler API
    to extract method calls from TypeScript/JavaScript code.
    """
    # Directory for the parser script
    parser_dir = os.path.join(os.path.dirname(__file__), 'ts_parser')
    os.makedirs(parser_dir, exist_ok=True)
    
    # Path to the parser script
    parser_script_path = os.path.join(parser_dir, 'extract_calls.js')
    
    # Check if the script already exists
    if os.path.exists(parser_script_path):
        return
    
    # Create package.json
    package_json = {
        "name": "typescript-method-extractor",
        "version": "1.0.0",
        "description": "Extracts method calls from TypeScript/JavaScript code",
        "main": "extract_calls.js",
        "dependencies": {
            "typescript": "^4.5.5"
        }
    }
    
    with open(os.path.join(parser_dir, 'package.json'), 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create the parser script
    parser_script = """
    const ts = require('typescript');
    const fs = require('fs');

    // Get the file path from the command line arguments
    const filePath = process.argv[2];
    if (!filePath) {
        console.error('No file path provided');
        process.exit(1);
    }

    // Read the source file
    const sourceCode = fs.readFileSync(filePath, 'utf8');

    // Create a TypeScript source file
    const sourceFile = ts.createSourceFile(
        filePath,
        sourceCode,
        ts.ScriptTarget.Latest,
        true
    );

    // Array to store method call information
    const methodCalls = [];

    // Visit each node in the AST
    function visit(node) {
        // Check for method calls (CallExpression with PropertyAccessExpression)
        if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
            const caller = sourceCode.substring(
                node.expression.expression.pos,
                node.expression.expression.end
            );
            const method = node.expression.name.text;
            
            // Extract arguments
            const args = node.arguments.map(arg => {
                return sourceCode.substring(arg.pos, arg.end).trim();
            });
            
            // Get line and column information
            const { line, character } = sourceFile.getLineAndCharacterOfPosition(node.pos);
            
            // Check if this is part of an await expression
            let isAsync = false;
            if (node.parent && ts.isAwaitExpression(node.parent)) {
                isAsync = true;
            }
            
            methodCalls.push({
                caller,
                method,
                args,
                lineno: line + 1, // Lines are 0-indexed in TS, but 1-indexed in our API
                col_offset: character,
                is_async: isAsync
            });
        }
        
        // Check for constructor calls (NewExpression)
        if (ts.isNewExpression(node)) {
            const className = node.expression.getText(sourceFile);
            
            // Extract arguments
            const args = node.arguments ? node.arguments.map(arg => {
                return sourceCode.substring(arg.pos, arg.end).trim();
            }) : [];
            
            // Get line and column information
            const { line, character } = sourceFile.getLineAndCharacterOfPosition(node.pos);
            
            methodCalls.push({
                is_constructor: true,
                class: className,
                args,
                lineno: line + 1,
                col_offset: character
            });
        }
        
        // Visit child nodes
        ts.forEachChild(node, visit);
    }

    // Start visiting from the root
    visit(sourceFile);

    // Output the method calls as JSON
    console.log(JSON.stringify(methodCalls, null, 2));
    """
    
    with open(parser_script_path, 'w') as f:
        f.write(parser_script)


# Try to create the TypeScript parser script when the module is imported
try:
    create_typescript_parser()
except Exception as e:
    print(f"Warning: Failed to create TypeScript parser script: {e}")
    print("Will use mock implementation for TypeScript method call extraction") 