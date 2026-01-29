#!/usr/bin/env python3
"""
Example application demonstrating the multi-domain agency system.
This shows how to use the system with various domains and features.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path so we can import the agency
sys.path.insert(0, str(Path(__file__).parent))

from agency import get_agency_components
from agency.core.base_domain import DomainInput


async def main():
    print("Initializing multi-domain agency...")
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    print("\nAvailable domains:")
    for domain in registry.get_all_domains():
        print(f"- {domain.name}: {domain.description}")

    print("\n" + "="*60)
    print("EXAMPLE 1: Code Generation")
    print("="*60)

    # Example 1: Code generation
    code_input = DomainInput(
        query="generate a python function that calculates fibonacci numbers",
        parameters={"language": "python"}
    )

    code_domain = registry.get_domain("code_generation")
    if code_domain and code_domain.can_handle(code_input):
        print(f"Executing code generation for: {code_input.query}")
        result = await code_domain.execute(code_input)

        if result.success:
            print("Generated code:")
            print(result.data["code"])
        else:
            print(f"Code generation failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 2: Documentation Generation")
    print("="*60)

    # Example 2: Documentation generation
    doc_input = DomainInput(
        query="create a README for a Python project named 'My Awesome Project'",
        parameters={"format": "markdown"}
    )

    doc_domain = registry.get_domain("documentation")
    if doc_domain and doc_domain.can_handle(doc_input):
        print(f"Generating documentation for: {doc_input.query}")
        result = await doc_domain.execute(doc_input)

        if result.success:
            print("Generated documentation:")
            print(result.data["documentation"][:500] + "..." if len(result.data["documentation"]) > 500 else result.data["documentation"])
        else:
            print(f"Documentation generation failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 3: Architecture Design")
    print("="*60)

    # Example 3: Architecture design
    arch_input = DomainInput(
        query="design a microservices architecture for an e-commerce platform",
        parameters={"pattern": "microservices", "cloud_platform": "aws"}
    )

    arch_domain = registry.get_domain("architecture")
    if arch_domain and arch_domain.can_handle(arch_input):
        print(f"Designing architecture for: {arch_input.query}")
        result = await arch_domain.execute(arch_input)

        if result.success:
            print("Architecture design:")
            print(result.data["architecture"][:500] + "..." if len(result.data["architecture"]) > 500 else result.data["architecture"])
        else:
            print(f"Architecture design failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 4: Cross-Domain Coordination")
    print("="*60)

    # Example 4: Cross-domain coordination
    print("Executing cross-domain workflow...")

    workflow = [
        {
            "domain": "research",
            "query": "research best practices for API design",
            "parameters": {"method": "literature_review"}
        },
        {
            "domain": "code_generation",
            "query": "generate a python API endpoint based on best practices for API design",
            "parameters": {"language": "python"}
        }
    ]

    workflow_result = await coordinator.execute_multi_domain_workflow(workflow)

    if workflow_result.success:
        print("Cross-domain workflow completed successfully!")
        print("Final result keys:", list(workflow_result.data.keys()))
    else:
        print(f"Cross-domain workflow failed: {workflow_result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 5: Skill Management")
    print("="*60)

    # Example 5: Skill management
    skill_mgmt_domain = registry.get_domain("skill_management")
    if skill_mgmt_domain:
        print("Listing available skills...")
        skill_list_input = DomainInput(
            query="list available skills",
            parameters={"target_agent": ""}
        )
        
        result = await skill_mgmt_domain.execute(skill_list_input)
        if result.success:
            print("Skills listed successfully")
            if "all_agents" in result.data:
                print(f"Found skills for {len(result.data['all_agents'])} agents")
        else:
            print(f"Skill listing failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 6: System Operations")
    print("="*60)

    # Example 6: System operations
    system_ops_domain = registry.get_domain("system_operations")
    if system_ops_domain:
        print("Performing system operations...")
        sys_op_input = DomainInput(
            query="list files in current directory",
            parameters={"path": ".", "recursive": False}
        )
        
        result = await system_ops_domain.execute(sys_op_input)
        if result.success:
            print("System operation completed successfully")
            if "items" in result.data.get("result", {}):
                items = result.data["result"]["items"]
                print(f"Found {len(items)} items in current directory")
                for item in items[:5]:  # Show first 5 items
                    print(f"  - {item['name']} ({item['type']})")
        else:
            print(f"System operation failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 7: Data Management")
    print("="*60)

    # Example 7: Data management
    data_mgmt_domain = registry.get_domain("data_management")
    if data_mgmt_domain:
        print("Performing data management operation...")
        data_input = DomainInput(
            query="perform research on data management best practices",
            parameters={"management_type": "research"}
        )
        
        result = await data_mgmt_domain.execute(data_input)
        if result.success:
            print("Data management operation completed successfully")
            if "result" in result.data:
                print("Operation summary available")
        else:
            print(f"Data management operation failed: {result.error}")

    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())