"""
AICK Studio Abandoned Cart Recovery Agent

This module contains the LangGraph-based agent for automated cart recovery.
"""

from .agent import AbandonedCartRecoveryAgent
from .state import AgentState, Cart, Customer, RecoveryAttempt

# Main function for running the recovery workflow
async def run_abandoned_cart_recovery(use_mock: bool = False, config: dict = None):
    """
    Run the abandoned cart recovery workflow.
    
    Args:
        use_mock: Whether to use mock data for testing
        config: Configuration parameters for the workflow
    
    Returns:
        dict: Recovery workflow results
    """
    agent = AbandonedCartRecoveryAgent()
    return await agent.run_recovery_workflow(use_mock=use_mock, config=config)

__all__ = [
    'AbandonedCartRecoveryAgent',
    'AgentState', 
    'Cart',
    'Customer',
    'RecoveryAttempt',
    'run_abandoned_cart_recovery'
]