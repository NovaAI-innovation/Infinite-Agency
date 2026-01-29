import asyncio
import unittest
from agency import get_agency_components
from agency.core.base_domain import DomainInput, DomainOutput
from agency.domains.code_generation.domain import CodeGenerationDomain
from agency.domains.research.domain import ResearchDomain
from agency.domains.documentation.domain import DocumentationDomain
from agency.domains.architecture.domain import ArchitectureDomain
from agency.domains.devops.domain import DevOpsDomain
from agency.domains.frontend.domain import FrontendDomain
from agency.domains.backend.domain import BackendDomain
from agency.domains.integrations.domain import IntegrationsDomain
from agency.domains.data_management.domain import DataManagementDomain
from agency.domains.communication.domain import CommunicationDomain
from agency.domains.preferences.domain import PreferencesDomain
from agency.domains.system_operations.domain import SystemOperationsDomain
from agency.domains.skill_management.domain import SkillManagementDomain


class TestMultiDomainAgency(unittest.TestCase):

    def setUp(self):
        components = get_agency_components()
        self.registry = components[0]
        self.coordinator = components[1]
        self.resource_manager = components[2]
        self.plugin_manager = components[3]
        self.config_manager = components[4]
        self.environment_manager = components[5]
        self.error_handling_manager = components[6]
        self.retry_executor = components[7]
        self.deployment_manager = components[8]
        self.deployment_orchestrator = components[9]
        self.task_lifecycle_manager = components[10]
        self.enhancement_pipeline = components[11]
        self.monitoring_service = components[12]
        self.health_checker = components[13]
        self.workflow_orchestrator = components[14]
        self.distributed_task_manager = components[15]
        self.security_manager = components[16]
        self.embedding_service = components[17]
        self.vector_store = components[18]
        self.knowledge_base = components[19]
        self.retriever = components[20]
        self.mcp_manager = components[21]
        self.decision_engine = components[22]
        self.context_manager = components[23]
        self.mcp_integration = components[24]

    def test_domain_registration(self):
        """Test that all domains are properly registered"""
        domains = self.registry.get_all_domains()
        expected_domains = {
            "code_generation", "research", "documentation", "architecture",
            "devops", "frontend", "backend", "integrations",
            "data_management", "communication", "preferences",
            "system_operations", "skill_management"
        }
        registered_domain_names = {domain.name for domain in domains}

        self.assertTrue(expected_domains.issubset(registered_domain_names),
                       f"Missing domains: {expected_domains - registered_domain_names}")

        # Test specific domains
        code_domain = self.registry.get_domain("code_generation")
        self.assertIsNotNone(code_domain)
        self.assertIsInstance(code_domain, CodeGenerationDomain)

        research_domain = self.registry.get_domain("research")
        self.assertIsNotNone(research_domain)
        self.assertIsInstance(research_domain, ResearchDomain)

        documentation_domain = self.registry.get_domain("documentation")
        self.assertIsNotNone(documentation_domain)
        self.assertIsInstance(documentation_domain, DocumentationDomain)

        architecture_domain = self.registry.get_domain("architecture")
        self.assertIsNotNone(architecture_domain)
        self.assertIsInstance(architecture_domain, ArchitectureDomain)

        devops_domain = self.registry.get_domain("devops")
        self.assertIsNotNone(devops_domain)
        self.assertIsInstance(devops_domain, DevOpsDomain)

        frontend_domain = self.registry.get_domain("frontend")
        self.assertIsNotNone(frontend_domain)
        self.assertIsInstance(frontend_domain, FrontendDomain)

        backend_domain = self.registry.get_domain("backend")
        self.assertIsNotNone(backend_domain)
        self.assertIsInstance(backend_domain, BackendDomain)

        integrations_domain = self.registry.get_domain("integrations")
        self.assertIsNotNone(integrations_domain)
        self.assertIsInstance(integrations_domain, IntegrationsDomain)

        data_management_domain = self.registry.get_domain("data_management")
        self.assertIsNotNone(data_management_domain)
        self.assertIsInstance(data_management_domain, DataManagementDomain)

        communication_domain = self.registry.get_domain("communication")
        self.assertIsNotNone(communication_domain)
        self.assertIsInstance(communication_domain, CommunicationDomain)

        preferences_domain = self.registry.get_domain("preferences")
        self.assertIsNotNone(preferences_domain)
        self.assertIsInstance(preferences_domain, PreferencesDomain)

        system_operations_domain = self.registry.get_domain("system_operations")
        self.assertIsNotNone(system_operations_domain)
        self.assertIsInstance(system_operations_domain, SystemOperationsDomain)

        skill_management_domain = self.registry.get_domain("skill_management")
        self.assertIsNotNone(skill_management_domain)
        self.assertIsInstance(skill_management_domain, SkillManagementDomain)

    def test_code_generation_domain(self):
        """Test the code generation domain"""
        code_domain = self.registry.get_domain("code_generation")

        # Test can_handle
        input_data = DomainInput(query="generate a python function")
        self.assertTrue(code_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await code_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("code", result.data)
            self.assertIn("language", result.data)

        asyncio.run(run_test())

    def test_research_domain(self):
        """Test the research domain"""
        research_domain = self.registry.get_domain("research")

        # Test can_handle
        input_data = DomainInput(query="research the benefits of microservices")
        self.assertTrue(research_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await research_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("results", result.data)
            self.assertIn("method", result.data)

        asyncio.run(run_test())

    def test_documentation_domain(self):
        """Test the documentation domain"""
        documentation_domain = self.registry.get_domain("documentation")

        # Test can_handle
        input_data = DomainInput(query="create a README for a Python project")
        self.assertTrue(documentation_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await documentation_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("documentation", result.data)

        asyncio.run(run_test())

    def test_architecture_domain(self):
        """Test the architecture domain"""
        architecture_domain = self.registry.get_domain("architecture")

        # Test can_handle
        input_data = DomainInput(query="design a microservices architecture")
        self.assertTrue(architecture_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await architecture_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("architecture", result.data)

        asyncio.run(run_test())

    def test_devops_domain(self):
        """Test the devops domain"""
        devops_domain = self.registry.get_domain("devops")

        # Test can_handle
        input_data = DomainInput(query="create a CI/CD pipeline")
        self.assertTrue(devops_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await devops_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("configuration", result.data)

        asyncio.run(run_test())

    def test_frontend_domain(self):
        """Test the frontend domain"""
        frontend_domain = self.registry.get_domain("frontend")

        # Test can_handle
        input_data = DomainInput(query="create a React component")
        self.assertTrue(frontend_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await frontend_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("code", result.data)

        asyncio.run(run_test())

    def test_backend_domain(self):
        """Test the backend domain"""
        backend_domain = self.registry.get_domain("backend")

        # Test can_handle
        input_data = DomainInput(query="create a REST API endpoint")
        self.assertTrue(backend_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await backend_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("code", result.data)

        asyncio.run(run_test())

    def test_integrations_domain(self):
        """Test the integrations domain"""
        integrations_domain = self.registry.get_domain("integrations")

        # Test can_handle
        input_data = DomainInput(query="integrate with Stripe API")
        self.assertTrue(integrations_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await integrations_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("code", result.data)

        asyncio.run(run_test())

    def test_data_management_domain(self):
        """Test the data management domain"""
        data_management_domain = self.registry.get_domain("data_management")

        # Test can_handle
        input_data = DomainInput(query="perform research on data management")
        self.assertTrue(data_management_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await data_management_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)
            self.assertIn("result", result.data)

        asyncio.run(run_test())

    def test_communication_domain(self):
        """Test the communication domain"""
        communication_domain = self.registry.get_domain("communication")

        # Test can_handle
        input_data = DomainInput(query="send a notification about task completion")
        self.assertTrue(communication_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await communication_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            # May not succeed due to missing recipient/config, but should not error
            self.assertIsNotNone(result)

        asyncio.run(run_test())

    def test_preferences_domain(self):
        """Test the preferences domain"""
        preferences_domain = self.registry.get_domain("preferences")

        # Test can_handle
        input_data = DomainInput(query="get notification preferences")
        self.assertTrue(preferences_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await preferences_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertIsNotNone(result)

        asyncio.run(run_test())

    def test_system_operations_domain(self):
        """Test the system operations domain"""
        system_ops_domain = self.registry.get_domain("system_operations")

        # Test can_handle
        input_data = DomainInput(query="list files in directory")
        self.assertTrue(system_ops_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await system_ops_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertIsNotNone(result)

        asyncio.run(run_test())

    def test_skill_management_domain(self):
        """Test the skill management domain"""
        skill_mgmt_domain = self.registry.get_domain("skill_management")

        # Test can_handle
        input_data = DomainInput(query="list available skills")
        self.assertTrue(skill_mgmt_domain.can_handle(input_data))

        # Test execute
        async def run_test():
            result = await skill_mgmt_domain.execute(input_data)
            self.assertIsInstance(result, DomainOutput)
            self.assertIsNotNone(result)

        asyncio.run(run_test())

    def test_cross_domain_workflow(self):
        """Test executing a workflow across multiple domains"""
        async def run_test():
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

            result = await self.coordinator.execute_multi_domain_workflow(workflow)
            self.assertIsInstance(result, DomainOutput)
            self.assertTrue(result.success)

        asyncio.run(run_test())

    def test_rag_system(self):
        """Test the RAG system components"""
        async def run_test():
            # Test adding a document to knowledge base
            doc_added = await self.knowledge_base.add_document(
                content="Test document for RAG system",
                metadata={"test": True, "category": "test"}
            )
            self.assertTrue(doc_added)

            # Test searching in the knowledge base
            search_results = await self.retriever.retrieve("test document", top_k=1)
            self.assertEqual(len(search_results), 1)
            self.assertGreaterEqual(search_results[0].score, 0.0)  # Score should be non-negative

        asyncio.run(run_test())

    def test_decision_engine(self):
        """Test the decision engine"""
        from agency.decision import DecisionContext, DecisionOutcome

        # Create a decision context
        context = DecisionContext(
            query="test decision making",
            domain="test_domain",
            available_resources={
                "cpu_percent": 50.0,
                "memory_mb": 512.0
            },
            historical_performance={
                "test_domain": {
                    "success_rate": 0.9,
                    "avg_response_time": 2.5
                }
            },
            current_state={"active_tasks": 1, "queue_length": 0},
            external_factors={"priority": "normal", "deadline": "flexible"}
        )

        # Make a decision
        decision_result = self.decision_engine.make_decision(context)
        self.assertIsNotNone(decision_result)
        self.assertIn(decision_result.outcome, [DecisionOutcome.APPROVED, DecisionOutcome.REJECTED,
                                               DecisionOutcome.DEFERRED, DecisionOutcome.NEEDS_MORE_INFO])
        self.assertGreaterEqual(decision_result.confidence, 0.0)
        self.assertLessEqual(decision_result.confidence, 1.0)
        self.assertIsInstance(decision_result.reasoning, str)
        self.assertIsInstance(decision_result.recommended_action, str)

    def test_context_manager(self):
        """Test the context manager"""
        async def run_test():
            # Create a conversation
            conversation_id = "test_conversation_1"
            participants = ["user1", "assistant1"]
            tags = ["test", "demo"]

            conversation = await self.context_manager.create_conversation(conversation_id, participants, tags)
            self.assertIsNotNone(conversation)
            self.assertEqual(conversation.conversation_id, conversation_id)
            self.assertEqual(conversation.participants, participants)
            self.assertEqual(conversation.tags, tags)

            # Add a turn to the conversation
            await self.context_manager.add_turn(conversation_id, "user", "Hello, world!", {"test": True})

            # Get the conversation and verify the turn was added
            retrieved_conversation = await self.context_manager.get_conversation(conversation_id)
            self.assertEqual(len(retrieved_conversation.turns), 1)
            self.assertEqual(retrieved_conversation.turns[0].role, "user")
            self.assertEqual(retrieved_conversation.turns[0].content, "Hello, world!")

            # Get recent turns
            recent_turns = await self.context_manager.get_recent_turns(conversation_id, count=1)
            self.assertEqual(len(recent_turns), 1)

            # Update metadata
            await self.context_manager.update_metadata(conversation_id, {"status": "active"})
            updated_conversation = await self.context_manager.get_conversation(conversation_id)
            self.assertEqual(updated_conversation.metadata["status"], "active")

        asyncio.run(run_test())

    def test_resource_management(self):
        """Test the resource management system"""
        # Test quota setting
        self.resource_manager.set_quota(
            "test_domain",
            self.resource_manager.ResourceQuota(
                cpu_percent=50.0,
                memory_mb=256,
                max_concurrent_tasks=5
            )
        )

        quota = self.resource_manager.get_quota("test_domain")
        self.assertIsNotNone(quota)
        self.assertEqual(quota.cpu_percent, 50.0)
        self.assertEqual(quota.memory_mb, 256)
        self.assertEqual(quota.max_concurrent_tasks, 5)

        # Test resource acquisition and release
        acquired = asyncio.run(self.resource_manager.acquire_resources("test_domain"))
        self.assertTrue(acquired)

        self.resource_manager.release_resources("test_domain")


if __name__ == "__main__":
    unittest.main()