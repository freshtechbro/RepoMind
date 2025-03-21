# Sequence Diagram Generation

This module provides functionality for generating sequence diagrams from source code. It supports Python and TypeScript/JavaScript code analysis and produces diagrams in Mermaid.js syntax.

## Features

- **Python Code Analysis**: Extracts method calls and object creations from Python code using the AST module
- **TypeScript/JavaScript Analysis**: Extracts method calls and object instantiations from TypeScript/JavaScript code
- **Sequence Diagram Generation**: Produces Mermaid.js syntax for sequence diagrams
- **Method Call Enhancement**: Infers missing information such as callee objects from method names
- **Support for Special Patterns**:
  - Asynchronous operations (async/await)
  - Conditional blocks
  - Object creation
  - Return values

## Usage

### API Endpoints

The following API endpoints are available for generating sequence diagrams:

#### Generate Sequence Diagram

```
POST /api/diagrams/sequence
```

Request body:
```json
{
  "code": "def test():\n    obj = MyClass()\n    obj.method()",
  "language": "python",
  "diagram_type": "sequence"
}
```

Response:
```json
{
  "diagram": "sequenceDiagram\n    participant test\n    participant MyClass\n    test->>+MyClass: new MyClass()\n    test->>MyClass: method()",
  "diagram_type": "sequence",
  "metadata": {
    "language": "python",
    "syntax": "mermaid"
  }
}
```

#### Analyze Code (Auto-select Diagram Type)

```
POST /api/diagrams/analyze
```

Request body:
```json
{
  "code": "class UserService {\n  async getUsers() {\n    return this.api.fetch('/users');\n  }\n}",
  "language": "typescript"
}
```

### Programmatic Usage

#### Python Code Analysis

```python
from app.diagrams.sequence.analyzer import analyze_python_code

# Analyze Python code
code = """
def process_data(data):
    validator = Validator()
    if validator.validate(data):
        processor = DataProcessor()
        result = processor.process(data)
        return result
    return None
"""

# Generate sequence diagram
mermaid_syntax = analyze_python_code(code)
print(mermaid_syntax)
```

#### TypeScript/JavaScript Code Analysis

```python
from app.diagrams.sequence.typescript_analyzer import analyze_typescript_code

# Analyze TypeScript code
code = """
class UserService {
    constructor(private api: ApiClient) {}
    
    async getUsers() {
        const response = await this.api.get('/users');
        return response.data;
    }
}
"""

# Generate sequence diagram
mermaid_syntax = analyze_typescript_code(code)
print(mermaid_syntax)
```

## Rendering Diagrams

The generated Mermaid.js syntax can be rendered using any Mermaid-compatible renderer:

- [Mermaid Live Editor](https://mermaid.live)
- [GitHub Markdown](https://github.blog/2022-02-14-include-diagrams-markdown-files-mermaid/) (supports Mermaid natively)
- [Visual Studio Code with Mermaid extension](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
- Any web application using the [Mermaid.js library](https://mermaid-js.github.io/mermaid/#/)

## Examples

### Python Example

Input:
```python
def authenticate_user(username, password):
    user_service = UserService()
    user = user_service.find_user(username)
    if user and user.check_password(password):
        token_service = TokenService()
        token = token_service.generate_token(user.id)
        return token
    return None
```

Generated Diagram:
```
sequenceDiagram
    participant authenticate_user
    participant UserService
    participant User
    participant TokenService
    authenticate_user->>+UserService: new UserService()
    authenticate_user->>UserService: find_user(username)
    UserService-->>authenticate_user: return user
    authenticate_user->>User: check_password(password)
    User-->>authenticate_user: return True/False
    alt if user and password check passes
        authenticate_user->>+TokenService: new TokenService()
        authenticate_user->>TokenService: generate_token(user.id)
        TokenService-->>authenticate_user: return token
    end
```

### TypeScript Example

Input:
```typescript
async function loadUserProfile(userId) {
    const userService = new UserService();
    try {
        const user = await userService.getUserById(userId);
        const preferences = await userService.getUserPreferences(userId);
        
        return {
            ...user,
            preferences
        };
    } catch (error) {
        logger.error(`Failed to load user profile: ${error.message}`);
        return null;
    }
}
```

Generated Diagram:
```
sequenceDiagram
    participant loadUserProfile
    participant UserService
    participant Logger
    loadUserProfile->>+UserService: new UserService()
    loadUserProfile-)UserService: getUserById(userId)
    UserService-->>loadUserProfile: return user
    loadUserProfile-)UserService: getUserPreferences(userId)
    UserService-->>loadUserProfile: return preferences
    alt if error occurs
        loadUserProfile->>Logger: error(message)
    end
```

## Limitations

- **TypeScript Analysis**: The TypeScript analysis depends on Node.js and the TypeScript compiler if using the full implementation. A simplified mock implementation is provided for environments without Node.js.
- **Complex Patterns**: Some complex language patterns may not be correctly extracted, especially in the mock implementation.
- **Inference Accuracy**: The callee inference is based on heuristics and may not always be accurate.
- **Visualization Complexity**: Very large code samples may produce diagrams that are difficult to read.

## Future Enhancements

- Support for more languages (Java, Go, Ruby)
- Enhanced visualization of complex patterns (loops, recursion)
- Better handling of inheritance and polymorphism
- Integration with more diagram rendering options
- Interactive diagram editing 