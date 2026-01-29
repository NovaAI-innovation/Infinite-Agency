from typing import Dict, Any, List, Optional, Callable
import asyncio
import unittest
import pytest
import time
from datetime import datetime
import json
import tempfile
import os
from pathlib import Path
import coverage

from agency.core.base_domain import BaseDomain, DomainInput, DomainOutput
from agency.core.domain_registry import DomainRegistry
from agency.core.coordinator import CrossDomainCoordinator
from agency.core.task_lifecycle import TaskLifecycleManager
from agency.core.workflow_engine import WorkflowOrchestrator, WorkflowBuilder
from agency.core.security import SecurityManager, Permission
from agency.core.advanced_monitoring import MonitoringService
from agency.core.error_handling import AsyncRetryExecutor, ErrorHandlingManager
from agency.core.distributed_task_execution import DistributedTaskManager
from agency.core.environment import EnvironmentManager

from agency.domains.code_generation.domain import CodeGenerationDomain
from agency.domains.research.domain import ResearchDomain

from agency.utils.logger import get_logger


class TestResult:
    """Represents the result of a test"""
    def __init__(self, name: str, success: bool, duration: float, error: str = None, details: Dict[str, Any] = None):
        self.name = name
        self.success = success
        self.duration = duration
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.now()


class TestSuite:
    """A suite of tests for a specific component or functionality"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tests: List[Callable] = []
        self.results: List[TestResult] = []
    
    def add_test(self, test_func: Callable):
        """Add a test function to the suite"""
        self.tests.append(test_func)
    
    async def run(self) -> List[TestResult]:
        """Run all tests in the suite"""
        self.results = []
        
        for test_func in self.tests:
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                duration = time.time() - start_time
                self.results.append(TestResult(test_func.__name__, True, duration))
            except Exception as e:
                duration = time.time() - start_time
                self.results.append(TestResult(test_func.__name__, False, duration, str(e)))
        
        return self.results


class IntegrationTestSuite(TestSuite):
    """Specialized test suite for integration tests"""
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.setup_funcs: List[Callable] = []
        self.teardown_funcs: List[Callable] = []
    
    def add_setup(self, setup_func: Callable):
        """Add a setup function to run before tests"""
        self.setup_funcs.append(setup_func)
    
    def add_teardown(self, teardown_func: Callable):
        """Add a teardown function to run after tests"""
        self.teardown_funcs.append(teardown_func)
    
    async def run(self) -> List[TestResult]:
        """Run all tests with setup and teardown"""
        # Run setup functions
        for setup_func in self.setup_funcs:
            if asyncio.iscoroutinefunction(setup_func):
                await setup_func()
            else:
                setup_func()
        
        # Run tests
        results = await super().run()
        
        # Run teardown functions
        for teardown_func in self.teardown_funcs:
            if asyncio.iscoroutinefunction(teardown_func):
                await teardown_func()
            else:
                teardown_func()
        
        return results


class TestRunner:
    """Runs tests and collects results"""
    def __init__(self):
        self.suites: List[TestSuite] = []
        self.all_results: List[TestResult] = []
        self._logger = get_logger(__name__)
    
    def add_suite(self, suite: TestSuite):
        """Add a test suite to the runner"""
        self.suites.append(suite)
    
    async def run_all(self) -> Dict[str, Any]:
        """Run all test suites and return results"""
        start_time = time.time()
        
        for suite in self.suites:
            self._logger.info(f"Running test suite: {suite.name}")
            results = await suite.run()
            self.all_results.extend(results)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        total_tests = len(self.all_results)
        passed_tests = sum(1 for r in self.all_results if r.success)
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error
                }
                for r in self.all_results
            ]
        }
        
        return summary
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a test report"""
        summary = {
            "total_tests": len(self.all_results),
            "passed": sum(1 for r in self.all_results if r.success),
            "failed": sum(1 for r in self.all_results if not r.success),
            "results": [r.__dict__ for r in self.all_results]
        }
        
        report = f"""
# Test Report

**Generated at:** {datetime.now().isoformat()}

## Summary
- Total Tests: {summary['total_tests']}
- Passed: {summary['passed']}
- Failed: {summary['failed']}
- Success Rate: {(summary['passed']/summary['total_tests']*100):.2f}% if {summary['total_tests']} > 0 else 0%

## Test Results
"""
        
        for result in self.all_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report += f"- {status} {result.name} ({result.duration:.2f}s)\n"
            if not result.success:
                report += f"  - Error: {result.error}\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
        
        return report


class ComponentTester:
    """Provides testing utilities for specific components"""
    
    @staticmethod
    def create_test_agency_components():
        """Create agency components for testing"""
        registry = DomainRegistry()
        security_manager = SecurityManager()
        monitoring_service = MonitoringService()
        error_handling_manager = ErrorHandlingManager()
        retry_executor = AsyncRetryExecutor(error_handling_manager)
        
        # Register test domains
        registry.register_domain_type("code_generation", CodeGenerationDomain)
        registry.register_domain_type("research", ResearchDomain)
        
        code_gen_domain = registry.create_and_register_domain(
            "code_generation", 
            "code_generation",
            description="Test code generation domain"
        )
        
        research_domain = registry.create_and_register_domain(
            "research", 
            "research", 
            description="Test research domain"
        )
        
        coordinator = CrossDomainCoordinator(registry)
        task_manager = TaskLifecycleManager()
        workflow_orchestrator = WorkflowOrchestrator(task_manager)
        distributed_task_manager = DistributedTaskManager()
        
        return {
            "registry": registry,
            "coordinator": coordinator,
            "security_manager": security_manager,
            "monitoring_service": monitoring_service,
            "error_handling_manager": error_handling_manager,
            "retry_executor": retry_executor,
            "task_manager": task_manager,
            "workflow_orchestrator": workflow_orchestrator,
            "distributed_task_manager": distributed_task_manager,
            "domains": {
                "code_generation": code_gen_domain,
                "research": research_domain
            }
        }
    
    @staticmethod
    async def test_domain_functionality(domain: BaseDomain, test_inputs: List[DomainInput]) -> List[DomainOutput]:
        """Test a domain with multiple inputs"""
        results = []
        for input_data in test_inputs:
            if domain.can_handle(input_data):
                result = await domain.execute(input_data)
                results.append(result)
            else:
                results.append(DomainOutput(success=False, error="Domain cannot handle input"))
        return results
    
    @staticmethod
    async def test_security_permissions(security_manager, username, password, required_permissions: List[Permission]):
        """Test security permissions for a user"""
        user = security_manager.authenticate_basic(username, password)
        results = {}
        for perm in required_permissions:
            results[perm.value] = security_manager.check_permission(user, perm)
        return results


def create_unit_test_suite() -> TestSuite:
    """Create a unit test suite for core components"""
    suite = TestSuite("Unit Tests", "Tests for individual components")
    
    async def test_domain_registry():
        """Test domain registry functionality"""
        registry = DomainRegistry()
        
        # Test registration
        registry.register_domain_type("test_domain", CodeGenerationDomain)
        assert "test_domain" in registry._domain_types
        
        # Test creation
        domain = registry.create_and_register_domain("test_instance", "test_domain")
        assert domain is not None
        assert domain.name == "test_instance"
    
    async def test_base_domain():
        """Test base domain functionality"""
        from agency.core.base_domain import DomainInput, DomainOutput
        
        input_data = DomainInput(query="test query", context={"test": True})
        assert input_data.query == "test query"
        assert input_data.context["test"] is True
        
        output_data = DomainOutput(success=True, data={"result": "test"})
        assert output_data.success is True
        assert output_data.data["result"] == "test"
    
    async def test_error_handling():
        """Test error handling functionality"""
        from agency.core.error_handling import ErrorHandlingManager, RetryPolicy, RetryStrategy
        
        manager = ErrorHandlingManager()
        policy = RetryPolicy(max_attempts=3, strategy=RetryStrategy.FIXED_INTERVAL)
        
        # Register handlers
        from agency.core.error_handling import TransientErrorHandler, ErrorCategory
        handler = TransientErrorHandler(policy)
        manager.register_handler(ErrorCategory.TRANSIENT, handler)
        
        # Verify handler is registered
        retrieved_handler = manager.get_handler(ErrorCategory.TRANSIENT)
        assert retrieved_handler is not None
    
    suite.add_test(test_domain_registry)
    suite.add_test(test_base_domain)
    suite.add_test(test_error_handling)
    
    return suite


def create_integration_test_suite() -> IntegrationTestSuite:
    """Create an integration test suite"""
    suite = IntegrationTestSuite("Integration Tests", "Tests for component interactions")
    
    # Setup function
    async def setup_agency():
        """Setup agency components for integration tests"""
        components = ComponentTester.create_test_agency_components()
        suite.agency_components = components
    
    # Teardown function
    async def teardown_agency():
        """Teardown agency components"""
        if hasattr(suite, 'agency_components'):
            # Shutdown any running services
            pass
    
    suite.add_setup(setup_agency)
    suite.add_teardown(teardown_agency)
    
    async def test_cross_domain_coordination():
        """Test cross-domain coordination"""
        components = suite.agency_components
        coordinator = components["coordinator"]
        
        workflow = [
            {
                "domain": "research",
                "query": "test research query",
                "parameters": {"method": "literature_review"}
            },
            {
                "domain": "code_generation", 
                "query": "test code generation query",
                "parameters": {"language": "python"}
            }
        ]
        
        result = await coordinator.execute_multi_domain_workflow(workflow)
        assert result is not None
    
    async def test_workflow_execution():
        """Test workflow execution"""
        components = suite.agency_components
        workflow_orch = components["workflow_orchestrator"]
        
        from agency.core.workflow_engine import WorkflowBuilder
        builder = WorkflowBuilder()
        workflow_def = (builder
            .create_workflow("test_workflow", "Test Workflow")
            .add_task("task1", "Test Task", "research", {
                "query": "test research",
                "parameters": {"method": "literature_review"}
            })
            .set_end_nodes(["task1"])
            .build()
        )
        
        workflow_orch.register_definition(workflow_def)
        instance_id = workflow_orch.create_instance("test_workflow")
        
        # Start and wait for completion
        await workflow_orch.start_instance(instance_id)
        await asyncio.sleep(0.5)  # Give it time to complete
        
        status = await workflow_orch.get_instance_status(instance_id)
        assert status is not None
    
    async def test_security_integration():
        """Test security integration"""
        components = suite.agency_components
        sec_man = components["security_manager"]
        
        # Create a user
        user = sec_man.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            permissions=[Permission.READ, Permission.EXECUTE]
        )
        
        # Authenticate
        authenticated_user = sec_man.authenticate_basic("testuser", "testpass123")
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"
        
        # Test permissions
        has_perm = sec_man.check_permission(authenticated_user, Permission.EXECUTE)
        assert has_perm is True
    
    suite.add_test(test_cross_domain_coordination)
    suite.add_test(test_workflow_execution)
    suite.add_test(test_security_integration)
    
    return suite


def create_performance_test_suite() -> TestSuite:
    """Create a performance test suite"""
    suite = TestSuite("Performance Tests", "Tests for performance and scalability")
    
    async def test_concurrent_execution():
        """Test concurrent execution of multiple tasks"""
        components = ComponentTester.create_test_agency_components()
        task_manager = components["task_manager"]
        
        # Register domains with task manager
        for name, domain in components["domains"].items():
            task_manager.register_domain_for_tasks(domain)
        
        # Submit multiple concurrent tasks
        tasks = []
        for i in range(5):
            task_id = await task_manager.execute_task(
                "code_generation",
                DomainInput(
                    query=f"generate function {i}",
                    parameters={"language": "python"}
                )
            )
            tasks.append(task_id)
        
        # Wait for all tasks to complete
        await asyncio.sleep(2)
        
        # Verify all tasks completed
        assert len(tasks) == 5
    
    async def test_error_recovery():
        """Test error recovery mechanisms"""
        from agency.core.error_handling import get_error_handling_manager, get_retry_executor
        
        error_man = get_error_handling_manager()
        retry_exec = get_retry_executor()
        
        # Create a function that fails initially but succeeds on retry
        attempt_count = 0
        def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        # Execute with retry
        result = await retry_exec.execute_with_retry(
            lambda: flaky_function(),
            error_category="transient"
        )
        
        assert result == "success"
        assert attempt_count >= 3  # Should have retried at least twice
    
    suite.add_test(test_concurrent_execution)
    suite.add_test(test_error_recovery)
    
    return suite


def run_comprehensive_tests(output_report: str = "test_report.md") -> Dict[str, Any]:
    """Run all tests and generate a comprehensive report"""
    runner = TestRunner()
    
    # Add all test suites
    runner.add_suite(create_unit_test_suite())
    runner.add_suite(create_integration_test_suite())
    runner.add_suite(create_performance_test_suite())
    
    # Run all tests
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    summary = loop.run_until_complete(runner.run_all())
    
    # Generate report
    report = runner.generate_report(output_report)
    
    return summary


if __name__ == "__main__":
    # Run the comprehensive tests
    summary = run_comprehensive_tests()
    
    print(f"Tests completed!")
    print(f"Total: {summary['total_tests']}, Passed: {summary['passed']}, Failed: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']*100:.2f}%")