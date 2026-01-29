"""
Decision engine for enhanced agent behavior.
Provides improved decision-making capabilities for agents.
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import json
from ..utils.logger import get_logger


class DecisionOutcome(Enum):
    """Possible outcomes of a decision"""
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    NEEDS_MORE_INFO = "needs_more_info"


@dataclass
class DecisionContext:
    """Context for making decisions"""
    query: str
    domain: str
    available_resources: Dict[str, Any]
    historical_performance: Dict[str, float]
    current_state: Dict[str, Any]
    external_factors: Dict[str, Any]


@dataclass
class DecisionResult:
    """Result of a decision"""
    outcome: DecisionOutcome
    confidence: float
    reasoning: str
    recommended_action: str
    metadata: Dict[str, Any]


class DecisionPolicy(ABC):
    """Abstract base class for decision policies"""
    
    @abstractmethod
    def evaluate(self, context: DecisionContext) -> DecisionResult:
        """Evaluate the context and return a decision result"""
        pass


class ResourceAwarePolicy(DecisionPolicy):
    """Policy that considers resource availability in decisions"""
    
    def evaluate(self, context: DecisionContext) -> DecisionResult:
        """Evaluate based on resource availability"""
        available_cpu = context.available_resources.get("cpu_percent", 100)
        available_memory = context.available_resources.get("memory_mb", 1000)
        
        # Define thresholds
        cpu_threshold = 80.0
        memory_threshold = 800.0
        
        if available_cpu < 20 or available_memory < 100:
            return DecisionResult(
                outcome=DecisionOutcome.REJECTED,
                confidence=0.9,
                reasoning="Insufficient resources to execute task",
                recommended_action="Wait for resources to become available or escalate to human operator",
                metadata={"available_cpu": available_cpu, "available_memory": available_memory}
            )
        elif available_cpu < cpu_threshold or available_memory < memory_threshold:
            return DecisionResult(
                outcome=DecisionOutcome.DEFERRED,
                confidence=0.7,
                reasoning="Resources are limited but task may be possible",
                recommended_action="Queue task for later execution when resources are available",
                metadata={"available_cpu": available_cpu, "available_memory": available_memory}
            )
        else:
            return DecisionResult(
                outcome=DecisionOutcome.APPROVED,
                confidence=0.95,
                reasoning="Sufficient resources available for task execution",
                recommended_action="Proceed with task execution",
                metadata={"available_cpu": available_cpu, "available_memory": available_memory}
            )


class HistoricalPerformancePolicy(DecisionPolicy):
    """Policy that considers historical performance in decisions"""
    
    def evaluate(self, context: DecisionContext) -> DecisionResult:
        """Evaluate based on historical performance"""
        domain_performance = context.historical_performance.get(context.domain, {})
        success_rate = domain_performance.get("success_rate", 0.0)
        avg_response_time = domain_performance.get("avg_response_time", 0.0)
        
        if success_rate < 0.5:
            return DecisionResult(
                outcome=DecisionOutcome.NEEDS_MORE_INFO,
                confidence=0.8,
                reasoning="Historical success rate for this domain is low",
                recommended_action="Request additional context or escalate to human operator",
                metadata={"success_rate": success_rate, "domain": context.domain}
            )
        elif success_rate < 0.8 or avg_response_time > 10.0:  # 10 seconds
            return DecisionResult(
                outcome=DecisionOutcome.DEFERRED,
                confidence=0.6,
                reasoning="Domain has suboptimal historical performance",
                recommended_action="Consider alternative approaches or schedule for off-peak time",
                metadata={"success_rate": success_rate, "avg_response_time": avg_response_time}
            )
        else:
            return DecisionResult(
                outcome=DecisionOutcome.APPROVED,
                confidence=0.9,
                reasoning="Domain has good historical performance",
                recommended_action="Proceed with task execution",
                metadata={"success_rate": success_rate, "avg_response_time": avg_response_time}
            )


class MultiCriteriaDecisionEngine:
    """Decision engine that combines multiple policies"""
    
    def __init__(self):
        self.policies: List[DecisionPolicy] = [
            ResourceAwarePolicy(),
            HistoricalPerformancePolicy()
        ]
        self._logger = get_logger(__name__)
    
    def add_policy(self, policy: DecisionPolicy):
        """Add a policy to the decision engine"""
        self.policies.append(policy)
    
    def make_decision(self, context: DecisionContext) -> DecisionResult:
        """Make a decision based on all policies"""
        policy_results = []
        
        for policy in self.policies:
            try:
                result = policy.evaluate(context)
                policy_results.append(result)
            except Exception as e:
                self._logger.error(f"Error evaluating policy {policy.__class__.__name__}: {e}")
                # Add a default rejection result if policy evaluation fails
                policy_results.append(DecisionResult(
                    outcome=DecisionOutcome.REJECTED,
                    confidence=0.5,
                    reasoning=f"Policy evaluation failed: {str(e)}",
                    recommended_action="Reject task due to policy evaluation error",
                    metadata={"error": str(e)}
                ))
        
        # Aggregate results - for now, we'll use a simple majority approach
        # In a more sophisticated implementation, we could weight policies differently
        approved_count = sum(1 for r in policy_results if r.outcome == DecisionOutcome.APPROVED)
        rejected_count = sum(1 for r in policy_results if r.outcome == DecisionOutcome.REJECTED)
        deferred_count = sum(1 for r in policy_results if r.outcome == DecisionOutcome.DEFERRED)
        needs_info_count = sum(1 for r in policy_results if r.outcome == DecisionOutcome.NEEDS_MORE_INFO)
        
        # Determine final outcome based on majority
        total_results = len(policy_results)
        if approved_count > rejected_count and approved_count > deferred_count and approved_count > needs_info_count:
            final_outcome = DecisionOutcome.APPROVED
        elif rejected_count > approved_count and rejected_count > deferred_count and rejected_count > needs_info_count:
            final_outcome = DecisionOutcome.REJECTED
        elif deferred_count > approved_count and deferred_count > rejected_count and deferred_count > needs_info_count:
            final_outcome = DecisionOutcome.DEFERRED
        elif needs_info_count > approved_count and needs_info_count > rejected_count and needs_info_count > deferred_count:
            final_outcome = DecisionOutcome.NEEDS_MORE_INFO
        else:
            # In case of tie, default to APPROVED with lower confidence
            final_outcome = DecisionOutcome.APPROVED
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in policy_results) / len(policy_results) if policy_results else 0.0
        
        # Combine reasoning from all policies
        combined_reasoning = "; ".join([r.reasoning for r in policy_results])
        
        # For recommended action, use the one from the policy that contributed to the final outcome
        final_result = None
        for r in policy_results:
            if r.outcome == final_outcome:
                final_result = r
                break
        
        if not final_result:
            final_result = policy_results[0]  # Fallback to first result
        
        return DecisionResult(
            outcome=final_outcome,
            confidence=avg_confidence,
            reasoning=combined_reasoning,
            recommended_action=final_result.recommended_action,
            metadata={
                "policy_results": [r.outcome.value for r in policy_results],
                "policy_count": len(policy_results)
            }
        )


# Global decision engine instance
decision_engine = MultiCriteriaDecisionEngine()


def get_decision_engine() -> MultiCriteriaDecisionEngine:
    """Get the global decision engine instance"""
    return decision_engine