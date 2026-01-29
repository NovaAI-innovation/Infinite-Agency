from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import re


class DocumentationDomain(BaseDomain):
    """Domain responsible for generating project documentation"""

    def __init__(self, name: str = "documentation", description: str = "Generates project documentation including README, API docs, and technical guides", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.doc_types = [
            "readme", "api_docs", "technical_guide", "user_manual", 
            "architecture_doc", "installation_guide", "troubleshooting_guide"
        ]
        self.markup_formats = ["markdown", "rst", "asciidoc", "html"]
        self.documentation_templates = {
            "readme": self._generate_readme_template,
            "api_docs": self._generate_api_docs_template,
            "technical_guide": self._generate_technical_guide_template,
            "user_manual": self._generate_user_manual_template,
            "architecture_doc": self._generate_architecture_doc_template,
            "installation_guide": self._generate_installation_guide_template,
            "troubleshooting_guide": self._generate_troubleshooting_guide_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate documentation based on the input specification"""
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

                # Determine the type of documentation to generate
                doc_type = self._determine_doc_type(query)
                markup_format = params.get("format", context.get("format", "markdown"))

                if markup_format not in self.markup_formats:
                    return DomainOutput(
                        success=False,
                        error=f"Markup format '{markup_format}' not supported. Supported formats: {', '.join(self.markup_formats)}"
                    )

                # Generate the documentation
                generated_doc = self._generate_documentation(doc_type, query, markup_format, params)

                # Enhance the documentation if other domains are available
                enhanced_doc = await self._enhance_with_other_domains(generated_doc, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "documentation": enhanced_doc,
                        "format": markup_format,
                        "type": doc_type,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_doc != generated_doc
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Documentation generation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest documentation generation
        doc_keywords = [
            "generate documentation", "write documentation", "create readme", 
            "document", "readme", "api docs", "api documentation", 
            "technical guide", "user manual", "architecture doc", 
            "installation guide", "setup guide", "troubleshooting", 
            "how to use", "guide", "manual", "instructions"
        ]

        return any(keyword in query for keyword in doc_keywords)

    def _determine_doc_type(self, query: str) -> str:
        """Determine what type of documentation to generate based on the query"""
        if any(word in query for word in ["readme", "read me", "project overview"]):
            return "readme"
        elif any(word in query for word in ["api", "api docs", "api documentation", "endpoints"]):
            return "api_docs"
        elif any(word in query for word in ["technical guide", "tech guide", "implementation"]):
            return "technical_guide"
        elif any(word in query for word in ["user manual", "user guide", "how to use"]):
            return "user_manual"
        elif any(word in query for word in ["architecture", "arch doc", "system design"]):
            return "architecture_doc"
        elif any(word in query for word in ["install", "setup", "installation", "getting started"]):
            return "installation_guide"
        elif any(word in query for word in ["troubleshoot", "debug", "fix", "issues"]):
            return "troubleshooting_guide"
        else:
            return "readme"  # Default to readme

    def _generate_documentation(self, doc_type: str, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate documentation based on type, query, and format"""
        if doc_type in self.documentation_templates:
            return self.documentation_templates[doc_type](query, markup_format, params)
        else:
            return self._generate_generic_documentation(query, markup_format, params)

    def _generate_readme_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate a README template based on the query"""
        project_name = params.get("project_name", "My Project")
        
        if markup_format == "markdown":
            return f"""# {project_name}

{params.get('description', 'Brief description of the project.')}

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
# Installation instructions
pip install {project_name.lower().replace(' ', '-')}
```

## Usage

```python
# Example usage
from {project_name.lower().replace(' ', '_')} import main

if __name__ == "__main__":
    main()
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
"""
        else:
            return f"# {project_name}\n\nDocumentation for {project_name} in {markup_format} format."

    def _generate_api_docs_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate API documentation template based on the query"""
        if markup_format == "markdown":
            return """# API Documentation

## Base URL
`https://api.example.com/v1`

## Authentication
All API requests require an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### GET /users
Retrieve a list of users.

#### Parameters
- `limit` (optional): Number of users to return (default: 10)
- `offset` (optional): Number of users to skip (default: 0)

#### Response
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "total": 1
}
```

### POST /users
Create a new user.

#### Request Body
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com"
}
```

#### Response
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "created_at": "2023-01-01T00:00:00Z"
}
```

## Error Responses

All error responses follow this format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```
"""
        else:
            return f"API Documentation for {query} in {markup_format} format."

    def _generate_technical_guide_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate a technical guide template based on the query"""
        if markup_format == "markdown":
            return f"""# Technical Guide

## Overview
This document provides technical details about {query}.

## Architecture
The system is composed of the following components:
- Component 1
- Component 2
- Component 3

## Implementation Details
### Module 1
Description of module 1 functionality and implementation.

### Module 2
Description of module 2 functionality and implementation.

## Data Flow
1. Step 1
2. Step 2
3. Step 3

## Performance Considerations
- Consideration 1
- Consideration 2
- Consideration 3

## Security Measures
- Measure 1
- Measure 2
- Measure 3
"""
        else:
            return f"Technical Guide for {query} in {markup_format} format."

    def _generate_user_manual_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate a user manual template based on the query"""
        if markup_format == "markdown":
            return f"""# User Manual

## Getting Started
Welcome to the user manual for {query}. This guide will help you get started.

## Installation
Instructions for installing the software.

## Basic Usage
### Starting the Application
Steps to start the application.

### Main Features
Description of main features and how to use them.

## Advanced Features
Detailed instructions for advanced features.

## Troubleshooting
Common issues and solutions:
- Issue 1: Solution 1
- Issue 2: Solution 2
- Issue 3: Solution 3

## Support
Contact information for support.
"""
        else:
            return f"User Manual for {query} in {markup_format} format."

    def _generate_architecture_doc_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate an architecture document template based on the query"""
        if markup_format == "markdown":
            return """# System Architecture Document

## Overview
This document describes the system architecture for the project.

## High-Level Architecture
```
[Client] <---> [Load Balancer] <---> [Application Servers] <---> [Database]
                   |                      |
              [Caching Layer]         [Message Queue]
```

## Components
### Frontend
- Technologies: React, TypeScript
- Responsibilities: User interface, user interactions

### Backend
- Technologies: Python, FastAPI
- Responsibilities: Business logic, API endpoints

### Database
- Technology: PostgreSQL
- Responsibilities: Data persistence

### Message Queue
- Technology: Redis
- Responsibilities: Task queuing, background jobs

## Data Flow
1. User makes request to frontend
2. Frontend sends API request to backend
3. Backend processes request and interacts with database
4. Response is sent back to frontend

## Scalability Considerations
- Horizontal scaling of application servers
- Database read replicas
- Caching layer for frequently accessed data

## Security Considerations
- HTTPS encryption
- Input validation
- Authentication and authorization
- Regular security audits
"""
        else:
            return f"Architecture Document for {query} in {markup_format} format."

    def _generate_installation_guide_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate an installation guide template based on the query"""
        if markup_format == "markdown":
            return """# Installation Guide

## Prerequisites
- Operating System: Linux/macOS/Windows
- Python 3.8+
- Node.js 14+ (for frontend)
- PostgreSQL 12+

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/username/repository.git
cd repository
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://localhost:5432/mydb
SECRET_KEY=your-secret-key
DEBUG=False
```

### 6. Run Database Migrations
```bash
python manage.py migrate
```

### 7. Start the Application
Backend:
```bash
python manage.py runserver
```

Frontend:
```bash
cd frontend
npm start
```

## Post-Installation
- Verify the application is running at http://localhost:3000
- Run tests to ensure everything is working correctly
- Configure any additional services as needed
"""
        else:
            return f"Installation Guide for {query} in {markup_format} format."

    def _generate_troubleshooting_guide_template(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate a troubleshooting guide template based on the query"""
        if markup_format == "markdown":
            return """# Troubleshooting Guide

## Common Issues

### Application Won't Start
**Symptoms:** Application fails to start with error message.
**Possible Causes:**
- Missing dependencies
- Incorrect environment variables
- Database connection issues
**Solutions:**
- Check that all dependencies are installed
- Verify environment variables are set correctly
- Ensure database is running and accessible

### Database Connection Errors
**Symptoms:** Database connection errors in logs.
**Possible Causes:**
- Incorrect database URL
- Database server not running
- Authentication issues
**Solutions:**
- Verify database URL in environment variables
- Check that database server is running
- Confirm credentials are correct

### Slow Performance
**Symptoms:** Application responds slowly.
**Possible Causes:**
- Insufficient server resources
- Inefficient queries
- Caching issues
**Solutions:**
- Monitor server resources
- Optimize database queries
- Enable/disable caching as appropriate

### Authentication Failures
**Symptoms:** Users unable to log in.
**Possible Causes:**
- Incorrect credentials
- Expired tokens
- Account locked/disabled
**Solutions:**
- Verify credentials are correct
- Check token expiration
- Confirm account status

## Diagnostic Commands

### Check Application Status
```bash
# Check if application processes are running
ps aux | grep application_name
```

### View Logs
```bash
# View application logs
tail -f logs/application.log
```

### Database Connectivity
```bash
# Test database connection
python manage.py db check
```

## Getting Help

If you're unable to resolve an issue:
1. Check the application logs for error messages
2. Consult the documentation
3. Contact support at support@example.com
"""
        else:
            return f"Troubleshooting Guide for {query} in {markup_format} format."

    def _generate_generic_documentation(self, query: str, markup_format: str, params: Dict[str, Any]) -> str:
        """Generate generic documentation when specific type isn't determined"""
        if markup_format == "markdown":
            return f"""# Documentation

## Overview
This document provides information about: {query}

## Details
TODO: Add detailed information about the topic.

## Additional Information
TODO: Add any additional relevant information.
"""
        else:
            return f"Documentation for: {query} in {markup_format} format"

    async def _enhance_with_other_domains(self, generated_doc: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated documentation"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original documentation
        return generated_doc