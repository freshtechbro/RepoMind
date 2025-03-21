
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
    