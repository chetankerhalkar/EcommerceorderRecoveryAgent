"""
AICK Studio Abandoned Cart Recovery Agent

Main LangGraph agent class that orchestrates the abandoned cart recovery workflow.
"""

import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes.observe_cart import observe_abandoned_carts, observe_abandoned_carts_mock
from .nodes.retrieve_details import retrieve_cart_details, retrieve_cart_details_mock
from .nodes.plan_message import plan_recovery_message, plan_recovery_message_mock
from .nodes.send_email import send_recovery_email, send_recovery_email_mock
from .nodes.monitor_activity import monitor_return_activity, monitor_return_activity_mock

logger = logging.getLogger(__name__)


class AbandonedCartRecoveryAgent:
    """
    LangGraph-based agent for recovering abandoned shopping carts
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize the agent
        
        Args:
            use_mock: Whether to use mock functions for development/testing
        """
        self.use_mock = use_mock
        self.graph = self._build_graph()
        self.memory = MemorySaver()
        
        logger.info(f"Abandoned Cart Recovery Agent initialized (mock mode: {use_mock})")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        
        Returns:
            Configured StateGraph
        """
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Choose functions based on mock mode
        if self.use_mock:
            observe_fn = observe_abandoned_carts_mock
            retrieve_fn = retrieve_cart_details_mock
            plan_fn = plan_recovery_message_mock
            send_fn = send_recovery_email_mock
            monitor_fn = monitor_return_activity_mock
        else:
            observe_fn = observe_abandoned_carts
            retrieve_fn = retrieve_cart_details
            plan_fn = plan_recovery_message
            send_fn = send_recovery_email
            monitor_fn = monitor_return_activity
        
        # Add nodes
        workflow.add_node("observe_carts", observe_fn)
        workflow.add_node("retrieve_details", retrieve_fn)
        workflow.add_node("plan_message", plan_fn)
        workflow.add_node("send_email", send_fn)
        workflow.add_node("monitor_activity", monitor_fn)
        
        # Set entry point
        workflow.set_entry_point("observe_carts")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "observe_carts",
            self._should_proceed_with_cart,
            {
                "proceed": "retrieve_details",
                "skip": END
            }
        )
        
        workflow.add_conditional_edges(
            "retrieve_details",
            self._should_send_recovery,
            {
                "send": "plan_message",
                "skip": END
            }
        )
        
        workflow.add_edge("plan_message", "send_email")
        workflow.add_edge("send_email", "monitor_activity")
        workflow.add_edge("monitor_activity", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _should_proceed_with_cart(self, state: AgentState) -> str:
        """
        Determine if we should proceed with cart recovery
        
        Args:
            state: Current agent state
            
        Returns:
            "proceed" or "skip"
        """
        if state.error_message:
            logger.warning(f"Skipping due to error: {state.error_message}")
            return "skip"
        
        if not state.is_abandoned:
            logger.info("No abandoned cart found, skipping")
            return "skip"
        
        if not state.cart:
            logger.warning("No cart data available, skipping")
            return "skip"
        
        logger.info(f"Proceeding with cart recovery for cart: {state.cart.id}")
        return "proceed"
    
    def _should_send_recovery(self, state: AgentState) -> str:
        """
        Determine if we should send recovery email
        
        Args:
            state: Current agent state
            
        Returns:
            "send" or "skip"
        """
        if state.error_message:
            logger.warning(f"Skipping email due to error: {state.error_message}")
            return "skip"
        
        if not state.customer:
            logger.warning("No customer data available, skipping email")
            return "skip"
        
        if not state.customer.accepts_marketing:
            logger.info(f"Customer {state.customer.email} doesn't accept marketing, skipping")
            return "skip"
        
        # Check if we've already sent too many recovery emails
        if len(state.recovery_attempts) >= 3:
            logger.info(f"Maximum recovery attempts reached for {state.customer.email}")
            return "skip"
        
        logger.info(f"Sending recovery email to {state.customer.email}")
        return "send"
    
    async def run_recovery_workflow(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the complete abandoned cart recovery workflow
        
        Args:
            config: Optional configuration parameters
            
        Returns:
            Final workflow state
        """
        logger.info("Starting abandoned cart recovery workflow")
        
        # Initialize state
        initial_state = AgentState(config=config or {})
        
        try:
            # Run the workflow
            final_state = await self.graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": "recovery_session"}}
            )
            
            logger.info(f"Workflow completed. Success: {final_state.recovery_successful}")
            
            return {
                "success": True,
                "recovery_successful": final_state.recovery_successful,
                "cart_id": final_state.cart.id if final_state.cart else None,
                "customer_email": final_state.customer.email if final_state.customer else None,
                "email_sent": len(final_state.recovery_attempts) > 0,
                "returned_to_cart": final_state.returned_to_cart,
                "checkout_completed": final_state.checkout_completed,
                "workflow_duration": (
                    final_state.workflow_completed_at - final_state.workflow_started_at
                ).total_seconds() if final_state.workflow_completed_at and final_state.workflow_started_at else None,
                "error_message": final_state.error_message
            }
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def run_single_cart_recovery(self, cart_data: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run recovery workflow for a specific cart and customer
        
        Args:
            cart_data: Cart information
            customer_data: Customer information
            
        Returns:
            Workflow result
        """
        logger.info(f"Running recovery for specific cart: {cart_data.get('id')}")
        
        from .state import Cart, Customer, CartItem
        
        try:
            # Convert input data to our models
            cart_items = [
                CartItem(**item) for item in cart_data.get("line_items", [])
            ]
            
            cart = Cart(
                id=cart_data["id"],
                token=cart_data.get("token", ""),
                line_items=cart_items,
                total_price=cart_data["total_price"],
                currency=cart_data.get("currency", "USD"),
                created_at=cart_data["created_at"],
                updated_at=cart_data["updated_at"],
                item_count=cart_data["item_count"]
            )
            
            customer = Customer(**customer_data)
            
            # Initialize state with provided data
            initial_state = AgentState(
                cart=cart,
                customer=customer,
                is_abandoned=True,
                should_send_recovery=True,
                abandonment_minutes=15
            )
            
            # Skip to message planning since we have the data
            workflow_config = {"configurable": {"thread_id": f"recovery_{cart.id}"}}
            
            # Run from plan_message node
            state_after_planning = await self.graph.ainvoke(
                initial_state,
                config=workflow_config
            )
            
            return {
                "success": True,
                "recovery_successful": state_after_planning.recovery_successful,
                "cart_id": cart.id,
                "customer_email": customer.email,
                "email_sent": len(state_after_planning.recovery_attempts) > 0,
                "email_subject": state_after_planning.email_subject,
                "recovery_message": state_after_planning.recovery_message
            }
            
        except Exception as e:
            logger.error(f"Single cart recovery failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def get_workflow_status(self, thread_id: str = "recovery_session") -> Dict[str, Any]:
        """
        Get the current status of a workflow
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Workflow status information
        """
        try:
            # Get the latest state from memory
            config = {"configurable": {"thread_id": thread_id}}
            state = self.memory.get(config)
            
            if not state:
                return {"status": "not_found"}
            
            return {
                "status": "active" if not state.workflow_completed_at else "completed",
                "cart_id": state.cart.id if state.cart else None,
                "customer_email": state.customer.email if state.customer else None,
                "recovery_attempts": len(state.recovery_attempts),
                "recovery_successful": state.recovery_successful,
                "error_message": state.error_message
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {"status": "error", "error_message": str(e)}


# Utility functions for external use
async def run_abandoned_cart_recovery(use_mock: bool = False, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to run the abandoned cart recovery workflow
    
    Args:
        use_mock: Whether to use mock data for testing
        config: Optional configuration
        
    Returns:
        Workflow result
    """
    agent = AbandonedCartRecoveryAgent(use_mock=use_mock)
    return await agent.run_recovery_workflow(config)


def create_recovery_agent(use_mock: bool = False) -> AbandonedCartRecoveryAgent:
    """
    Factory function to create a recovery agent
    
    Args:
        use_mock: Whether to use mock data for testing
        
    Returns:
        Configured agent instance
    """
    return AbandonedCartRecoveryAgent(use_mock=use_mock)

