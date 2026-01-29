import asyncio
import unittest
from agency import get_agency_components
from agency.core.base_domain import DomainInput, DomainOutput
from agency.domains.code_generation.domain import CodeGenerationDomain
from agency.domains.research.domain import ResearchDomain


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
        """Test that domains are properly registered"""
        domains = self.registry.get_all_domains()
        self.assertGreaterEqual(len(domains), 2)  # At least code generation and research

        code_domain = self.registry.get_domain("code_generation")
        self.assertIsNotNone(code_domain)
        self.assertIsInstance(code_domain, CodeGenerationDomain)

        research_domain = self.registry.get_domain("research")
        self.assertIsNotNone(research_domain)
        self.assertIsInstance(research_domain, ResearchDomain)

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


if __name__ == "__main__":
    unittest.main()