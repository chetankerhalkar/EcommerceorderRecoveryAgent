"""
Agent API Routes

This module provides REST API endpoints for interacting with the
abandoned cart recovery agent.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field , EmailStr

from agent import AbandonedCartRecoveryAgent, run_abandoned_cart_recovery

logger = logging.getLogger(__name__)

router = APIRouter()

# Global agent instance
agent_instance: Optional[AbandonedCartRecoveryAgent] = None

class EmailRequest(BaseModel):
    email: EmailStr

class RecoveryRequest(BaseModel):
    """Request model for manual recovery trigger"""
    use_mock: bool = Field(default=False, description="Use mock data for testing")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Optional configuration")


class CartRecoveryRequest(BaseModel):
    """Request model for specific cart recovery"""
    cart: Dict[str, Any] = Field(..., description="Cart data")
    customer: Dict[str, Any] = Field(..., description="Customer data")
    use_mock: bool = Field(default=False, description="Use mock functions")


class AgentStatusResponse(BaseModel):
    """Response model for agent status"""
    status: str
    cart_id: Optional[str] = None
    customer_email: Optional[str] = None
    recovery_attempts: int = 0
    recovery_successful: bool = False
    error_message: Optional[str] = None


@router.post("/start-recovery")
async def start_recovery_workflow(
    request: RecoveryRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Start the abandoned cart recovery workflow
    
    Args:
        request: Recovery request parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Workflow initiation response
    """
    logger.info(f"Starting recovery workflow (mock: {request.use_mock})")
    
    try:
        # Run workflow in background
        background_tasks.add_task(
            run_abandoned_cart_recovery,
            use_mock=request.use_mock,
            config=request.config
        )
        
        return {
            "success": True,
            "message": "Recovery workflow started",
            "mock_mode": request.use_mock
        }
        
    except Exception as e:
        logger.error(f"Failed to start recovery workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recover-cart")
async def recover_specific_cart(request: CartRecoveryRequest) -> Dict[str, Any]:
    """
    Recover a specific abandoned cart
    
    Args:
        request: Cart recovery request
        
    Returns:
        Recovery result
    """
    logger.info(f"Recovering specific cart: {request.cart.get('id')}")
    
    try:
        agent = AbandonedCartRecoveryAgent(use_mock=request.use_mock)
        result = await agent.run_single_cart_recovery(
            cart_data=request.cart,
            customer_data=request.customer
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to recover cart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{thread_id}")
async def get_workflow_status(thread_id: str) -> AgentStatusResponse:
    """
    Get the status of a workflow
    
    Args:
        thread_id: Workflow thread identifier
        
    Returns:
        Workflow status
    """
    try:
        global agent_instance
        if not agent_instance:
            agent_instance = AbandonedCartRecoveryAgent()
        
        status = agent_instance.get_workflow_status(thread_id)
        
        return AgentStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_default_workflow_status() -> AgentStatusResponse:
    """
    Get the status of the default workflow
    
    Returns:
        Default workflow status
    """
    return await get_workflow_status("recovery_session")


@router.post("/test-email")
async def send_test_email(request: EmailRequest) -> Dict[str, Any]:
    """
    Send a test email to verify configuration
    """
    logger.info(f"Sending test email to: {request.email}")
    
    try:
        from agent.nodes.send_email import send_test_email
        success = send_test_email(request.email)
        
        return {
            "success": success,
            "message": "Test email sent successfully" if success else "Failed to send test email",
            "recipient": request.email
        }
        
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mock-data")
async def get_mock_data() -> Dict[str, Any]:
    """
    Get mock cart and customer data for testing
    
    Returns:
        Mock data
    """
    try:
        import json
        
        mock_file = r"C:\AICK\EcommerceorderRecoveryAgent\mock_data\cart.json"
        with open(mock_file, 'r') as f:
            mock_data = json.load(f)
        
        return {
            "success": True,
            "data": mock_data
        }
        
    except Exception as e:
        logger.error(f"Failed to load mock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-message")
async def generate_recovery_message(request: CartRecoveryRequest) -> Dict[str, Any]:
    """
    Generate a recovery message without sending email
    
    Args:
        request: Cart and customer data
        
    Returns:
        Generated message content
    """
    logger.info("Generating recovery message preview")
    
    try:
        from agent.nodes.plan_message import plan_recovery_message_mock
        from agent.state import AgentState, Cart, Customer, CartItem
        
        # Convert input data to our models
        cart_items = [
            CartItem(**item) for item in request.cart.get("line_items", [])
        ]
        
        cart = Cart(
            id=request.cart["id"],
            token=request.cart.get("token", ""),
            line_items=cart_items,
            total_price=request.cart["total_price"],
            currency=request.cart.get("currency", "USD"),
            created_at=request.cart["created_at"],
            updated_at=request.cart["updated_at"],
            item_count=request.cart["item_count"]
        )
        
        customer = Customer(**request.customer)
        
        # Create state
        state = AgentState(
            cart=cart,
            customer=customer,
            abandonment_minutes=15
        )
        
        # Generate message
        if request.use_mock:
            result = plan_recovery_message_mock(state)
        else:
            from ...agent.nodes.plan_message import plan_recovery_message
            result = await plan_recovery_message(state)
        
        return {
            "success": True,
            "email_subject": result.get("email_subject"),
            "recovery_message": result.get("recovery_message"),
            "email_html_content": result.get("email_html_content"),
            "error_message": result.get("error_message")
        }
        
    except Exception as e:
        logger.error(f"Failed to generate message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

