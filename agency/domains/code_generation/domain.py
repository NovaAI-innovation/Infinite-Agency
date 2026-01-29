from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import re


class CodeGenerationDomain(BaseDomain):
    """Domain responsible for generating code based on specifications"""

    def __init__(self, name: str = "code_generation", description: str = "Generates code in various programming languages", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "go",
            "rust", "c++", "c#", "php", "ruby", "swift", "kotlin"
        ]
        self.code_templates = {
            "function": self._generate_function_template,
            "class": self._generate_class_template,
            "api_endpoint": self._generate_api_endpoint_template,
            "test": self._generate_test_template
        }
    
    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate code based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of code to generate
                code_type = self._determine_code_type(query)
                language = params.get("language", context.get("language", "python"))

                if language not in self.supported_languages:
                    return DomainOutput(
                        success=False,
                        error=f"Language '{language}' not supported. Supported languages: {', '.join(self.supported_languages)}"
                    )

                # Generate the code
                generated_code = self._generate_code(code_type, query, language, params)

                # Enhance the code if other domains are available
                enhanced_code = await self._enhance_with_other_domains(generated_code, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "code": enhanced_code,
                        "language": language,
                        "type": code_type,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_code != generated_code
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Code generation failed: {str(e)}"
            )
    
    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()
        
        # Check for keywords that suggest code generation
        code_keywords = [
            "generate code", "write code", "implement", "function", 
            "class", "method", "algorithm", "program", "script",
            "create", "build", "develop", "code for", "make"
        ]
        
        return any(keyword in query for keyword in code_keywords) or \
               any(lang in query for lang in self.supported_languages)
    
    def _determine_code_type(self, query: str) -> str:
        """Determine what type of code to generate based on the query"""
        if any(word in query for word in ["function", "method", "def", "func"]):
            return "function"
        elif any(word in query for word in ["class", "object", "struct"]):
            return "class"
        elif any(word in query for word in ["api", "endpoint", "route", "controller"]):
            return "api_endpoint"
        elif any(word in query for word in ["test", "unit test", "spec"]):
            return "test"
        else:
            return "function"  # Default to function
    
    def _generate_code(self, code_type: str, query: str, language: str, params: Dict[str, Any]) -> str:
        """Generate code based on type, query, and language"""
        if code_type in self.code_templates:
            return self.code_templates[code_type](query, language, params)
        else:
            return self._generate_generic_code(query, language, params)
    
    def _generate_function_template(self, query: str, language: str, params: Dict[str, Any]) -> str:
        """Generate a function based on the query"""
        # Extract function name and parameters from query
        import re
        func_match = re.search(r"(?:function|method|func)\s+(\w+)", query)
        func_name = func_match.group(1) if func_match else "my_function"
        
        # Extract description of what the function should do
        desc_parts = query.split("function")[-1].split("that")[1:] if "that" in query else [query]
        description = " ".join(desc_parts).strip()
        
        templates = {
            "python": f"""def {func_name}():
    \"\"\"
    {description}
    \"\"\"
    # TODO: Implement function logic here
    pass""",
            
            "javascript": f"""function {func_name}() {{
    // {description}
    // TODO: Implement function logic here
}}""",
            
            "java": f"""public class CodeGen {{
    /**
     * {description}
     */
    public static void {func_name}() {{
        // TODO: Implement function logic here
    }}
}}""",
            
            "go": f"""package main

import "fmt"

// {description}
func {func_name}() {{
    // TODO: Implement function logic here
    fmt.Println("Function {func_name} called")
}}""",
        }
        
        return templates.get(language, f"// {func_name}: {description} in {language}")
    
    def _generate_class_template(self, query: str, language: str, params: Dict[str, Any]) -> str:
        """Generate a class based on the query"""
        import re
        class_match = re.search(r"(?:class|object)\s+(\w+)", query)
        class_name = class_match.group(1) if class_match else "MyClass"
        
        templates = {
            "python": f"""class {class_name}:
    def __init__(self):
        # Initialize class attributes
        pass
    
    def __str__(self):
        return f"{class_name} object"
    
    # TODO: Add methods as needed""",
            
            "javascript": f"""class {class_name} {{
    constructor() {{
        // Initialize class properties
    }}
    
    toString() {{
        return "{class_name} object";
    }}
    
    // TODO: Add methods as needed
}}""",
            
            "java": f"""public class {class_name} {{
    // Class attributes
    private String name;
    
    public {class_name}() {{
        // Initialize class attributes
    }}
    
    @Override
    public String toString() {{
        return "{class_name} object";
    }}
    
    // TODO: Add methods as needed
}}""",
        }
        
        return templates.get(language, f"// Class {class_name} in {language}")
    
    def _generate_api_endpoint_template(self, query: str, language: str, params: Dict[str, Any]) -> str:
        """Generate an API endpoint based on the query"""
        templates = {
            "python": """from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/example', methods=['GET'])
def get_example():
    # TODO: Implement endpoint logic
    return jsonify({"message": "Example endpoint"})

@app.route('/api/example', methods=['POST'])
def create_example():
    data = request.get_json()
    # TODO: Process incoming data
    return jsonify({"message": "Created", "data": data})

if __name__ == '__main__':
    app.run(debug=True)""",
            
            "javascript": """const express = require('express');
const app = express();

app.use(express.json());

app.get('/api/example', (req, res) => {
    // TODO: Implement endpoint logic
    res.json({ message: "Example endpoint" });
});

app.post('/api/example', (req, res) => {
    const data = req.body;
    // TODO: Process incoming data
    res.json({ message: "Created", data });
});

module.exports = app;""",
        }
        
        return templates.get(language, f"// API endpoint in {language}")
    
    def _generate_test_template(self, query: str, language: str, params: Dict[str, Any]) -> str:
        """Generate a test based on the query"""
        templates = {
            "python": """import unittest

class TestGenerated(unittest.TestCase):
    def test_example(self):
        # TODO: Implement test logic
        self.assertTrue(True)
    
    def test_another_case(self):
        # TODO: Add more test cases
        pass

if __name__ == '__main__':
    unittest.main()""",
            
            "javascript": """// Using Jest
describe('Generated Tests', () => {
    test('example test', () => {
        // TODO: Implement test logic
        expect(true).toBe(true);
    });
    
    test('another test case', () => {
        // TODO: Add more test cases
    });
});""",
        }
        
        return templates.get(language, f"// Test in {language}")
    
    def _generate_generic_code(self, query: str, language: str, params: Dict[str, Any]) -> str:
        """Generate generic code when specific type isn't determined"""
        return f"""// Generated code for: {query}
// Language: {language}
// TODO: Implement the requested functionality
"""
    
    async def _enhance_with_other_domains(self, generated_code: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated code"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original code
        return generated_code