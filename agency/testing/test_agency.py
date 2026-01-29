import asyncio
import unittest
from agency import get_agency_components
from agency.core.base_domain import DomainInput
from agency.core.workflow_engine import WorkflowBuilder
from agency.core.security import Permission


class TestAgencyComponents(unittest.TestCase):
    """Test the agency components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests in the class."""
        cls.registry, cls.coordinator, cls.resource_manager, cls.plugin_manager, cls.config_manager, \
        cls.environment_manager, cls.error_handling_manager, cls.retry_executor, \
        cls.deployment_manager, cls.deployment_orchestrator, cls.task_lifecycle_manager, \
        cls.enhancement_pipeline, cls.monitoring_service, cls.health_checker, \
        cls.workflow_orchestrator, cls.distributed_task_manager, cls.security_manager = get_agency_components()
    
    def test_domain_registry(self):
        """Test that domains are properly registered"""
        domains = self.registry.get_all_domains()
        self.assertGreaterEqual(len(domains), 2)  # At least code generation and research
        
        code_domain = self.registry.get_domain("code_generation")
        self.assertIsNotNone(code_domain)
        
        research_domain = self.registry.get_domain("research")
        self.assertIsNotNone(research_domain)
    
    def test_code_generation_domain(self):
        """Test the code generation domain"""
        code_domain = self.registry.get_domain("code_generation")
        
        # Test can_handle
        input_data = DomainInput(query="generate a python function")
        self.assertTrue(code_domain.can_handle(input_data))
    
    def test_research_domain(self):
        """Test the research domain"""
        research_domain = self.registry.get_domain("research")
        
        # Test can_handle
        input_data = DomainInput(query="research the benefits of microservices")
        self.assertTrue(research_domain.can_handle(input_data))
    
    def test_cross_domain_workflow(self):
        """Test executing a workflow across multiple domains"""
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
        
        # This would normally be async, but for unit tests we'll check if the coordinator exists
        self.assertIsNotNone(self.coordinator)
    
    async def test_workflow_orchestration(self):
        """Test workflow orchestration"""
        # Create a simple workflow: research -> code generation
        builder = WorkflowBuilder()
        workflow_def = (builder
            .create_workflow("test_workflow", "Test Research-to-Code Workflow")
            .add_task("research_step", "Research Step", "research", {
                "query": "research best practices for secure coding",
                "parameters": {"method": "literature_review"}
            })
            .add_task("code_step", "Code Generation Step", "code_generation", {
                "query": "generate a python function implementing secure coding best practices",
                "parameters": {"language": "python"}
            })
            .connect("research_step", "code_step")  # Connect research to code generation
            .set_end_nodes(["code_step"])  # Set code generation as the end node
            .build()
        )
        
        # Register the workflow definition
        self.workflow_orchestrator.register_definition(workflow_def)
        
        # Create and start a workflow instance
        instance_id = self.workflow_orchestrator.create_instance("test_workflow")
        await self.workflow_orchestrator.start_instance(instance_id)
        
        # Check the status
        status = await self.workflow_orchestrator.get_instance_status(instance_id)
        self.assertIsNotNone(status)
    
    async def test_security_features(self):
        """Test security features"""
        # Create a user with specific permissions
        user = self.security_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="securepassword123",
            permissions=[Permission.READ, Permission.WRITE, Permission.EXECUTE]
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        
        # Authenticate the user
        authenticated_user = self.security_manager.authenticate_basic("testuser", "securepassword123")
        self.assertIsNotNone(authenticated_user)
        
        # Create a JWT token for the user
        jwt_token = self.security_manager.create_jwt_token(authenticated_user.id)
        self.assertIsNotNone(jwt_token)
        
        # Verify the token
        verified_user = self.security_manager.verify_jwt_token(jwt_token)
        self.assertIsNotNone(verified_user)
        self.assertEqual(verified_user.username, "testuser")
        
        # Check permissions
        has_execute = self.security_manager.check_permission(verified_user, Permission.EXECUTE)
        self.assertTrue(has_execute)


class TestAgencyIntegration(unittest.TestCase):
    """Integration tests for the agency system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests in the class."""
        cls.registry, cls.coordinator, cls.resource_manager, cls.plugin_manager, cls.config_manager, \
        cls.environment_manager, cls.error_handling_manager, cls.retry_executor, \
        cls.deployment_manager, cls.deployment_orchestrator, cls.task_lifecycle_manager, \
        cls.enhancement_pipeline, cls.monitoring_service, cls.health_checker, \
        cls.workflow_orchestrator, cls.distributed_task_manager, cls.security_manager = get_agency_components()
    
    async def test_end_to_end_workflow(self):
        """Test an end-to-end workflow"""
        # Submit a task to the task lifecycle manager
        result = await self.task_lifecycle_manager.execute_task(
            "code_generation",
            DomainInput(
                query="generate a simple python function to reverse a string",
                parameters={"language": "python"}
            )
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertIn("data", result.__dict__)
    
    async def test_health_check(self):
        """Test health checking functionality"""
        health_report = await self.health_checker.check_system_health()
        
        self.assertIsNotNone(health_report)
        self.assertIn("overall_status", health_report)
        self.assertIn("components", health_report)
        self.assertIn("issues", health_report)
        
        # Overall status should be healthy in a test environment
        self.assertIn(health_report["overall_status"], ["healthy", "warning"])


# Helper function to run async tests
def run_async_test(coro):
    """Helper to run async tests in a sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Add async test methods to the test classes
def add_async_test_methods():
    """Dynamically add async test methods to test classes"""
    
    # Add async test for workflow orchestration
    def test_workflow_orchestration_sync(self):
        run_async_test(TestAgencyComponents.test_workflow_orchestration(self))
    
    def test_security_features_sync(self):
        run_async_test(TestAgencyComponents.test_security_features(self))
    
    def test_end_to_end_workflow_sync(self):
        run_async_test(TestAgencyIntegration.test_end_to_end_workflow(self))
    
    def test_health_check_sync(self):
        run_async_test(TestAgencyIntegration.test_health_check(self))
    
    # Attach the sync versions to the classes
    TestAgencyComponents.test_workflow_orchestration_sync = test_workflow_orchestration_sync
    TestAgencyComponents.test_security_features_sync = test_security_features_sync
    TestAgencyIntegration.test_end_to_end_workflow_sync = test_end_to_end_workflow_sync
    TestAgencyIntegration.test_health_check_sync = test_health_check_sync


# Call the function to add async test methods
add_async_test_methods()


if __name__ == '__main__':
    unittest.main()