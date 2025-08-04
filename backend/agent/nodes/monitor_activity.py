"""
Activity Monitoring Node

This node monitors for return checkout activity and email engagement
to determine if the recovery campaign was successful.
"""

import os
import httpx
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

from ..state import AgentState

logger = logging.getLogger(__name__)


async def monitor_return_activity(state: AgentState) -> Dict[str, Any]:
    """
    Monitor for return checkout activity and email engagement
    
    Args:
        state: Current agent state with recovery attempt information
        
    Returns:
        Updated state with monitoring results
    """
    logger.info(f"Monitoring return activity for cart: {state.cart.id if state.cart else 'None'}")
    
    if not state.cart or not state.customer:
        return {"error_message": "Missing cart or customer information"}
    
    try:
        # Check for checkout completion
        checkout_completed = await check_checkout_completion(state)
        
        # Check for cart return activity
        returned_to_cart = await check_cart_return(state)
        
        # Check email engagement (if SendGrid webhooks are configured)
        email_engagement = await check_email_engagement(state)
        
        # Determine recovery success
        recovery_successful = checkout_completed or (returned_to_cart and email_engagement.get("clicked", False))
        
        logger.info(f"Monitoring results - Completed: {checkout_completed}, Returned: {returned_to_cart}, Success: {recovery_successful}")
        
        return {
            "returned_to_cart": returned_to_cart,
            "checkout_completed": checkout_completed,
            "recovery_successful": recovery_successful,
            "workflow_completed_at": datetime.now(),
            "config": {
                **state.config,
                "monitoring_completed": True,
                "email_engagement": email_engagement,
                "monitored_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error monitoring return activity: {str(e)}")
        return {"error_message": f"Error monitoring activity: {str(e)}"}


async def check_checkout_completion(state: AgentState) -> bool:
    """
    Check if the customer completed the checkout
    
    Args:
        state: Current agent state
        
    Returns:
        True if checkout was completed, False otherwise
    """
    try:
        # Get configuration
        shopify_url = os.getenv("SHOPIFY_SHOP_URL")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        api_version = os.getenv("SHOPIFY_API_VERSION", "2023-04")
        
        if not shopify_url or not access_token:
            logger.warning("Missing Shopify configuration for checkout monitoring")
            return False
        
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        # Check recent orders for this customer
        since_time = datetime.now() - timedelta(hours=24)  # Check last 24 hours
        orders_url = f"https://{shopify_url}/admin/api/{api_version}/orders.json"
        
        params = {
            "status": "any",
            "created_at_min": since_time.isoformat(),
            "limit": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(orders_url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Failed to check orders: {response.status_code}")
                return False
            
            data = response.json()
            orders = data.get("orders", [])
            
            # Check if any order matches our cart items
            for order in orders:
                if order.get("customer", {}).get("id") == state.customer.id:
                    # Check if order contains items from our abandoned cart
                    order_items = {item["variant_id"] for item in order.get("line_items", [])}
                    cart_items = {item.variant_id for item in state.cart.line_items}
                    
                    # If there's significant overlap, consider it a recovery
                    overlap = len(order_items.intersection(cart_items))
                    if overlap >= len(cart_items) * 0.5:  # 50% overlap threshold
                        logger.info(f"Found matching order: {order['id']}")
                        return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking checkout completion: {str(e)}")
        return False


async def check_cart_return(state: AgentState) -> bool:
    """
    Check if the customer returned to their cart
    
    Args:
        state: Current agent state
        
    Returns:
        True if customer returned to cart, False otherwise
    """
    try:
        # Get configuration
        shopify_url = os.getenv("SHOPIFY_SHOP_URL")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        api_version = os.getenv("SHOPIFY_API_VERSION", "2023-04")
        
        if not shopify_url or not access_token:
            logger.warning("Missing Shopify configuration for cart monitoring")
            return False
        
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        # Check if the checkout was updated recently
        checkout_url = f"https://{shopify_url}/admin/api/{api_version}/checkouts/{state.cart.id}.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(checkout_url, headers=headers)
            
            if response.status_code != 200:
                logger.warning(f"Failed to check cart return: {response.status_code}")
                return False
            
            data = response.json()
            checkout = data.get("checkout", {})
            
            # Check if updated_at is after our email was sent
            if state.current_attempt and state.current_attempt.sent_at:
                updated_at = datetime.fromisoformat(checkout["updated_at"].replace("Z", "+00:00"))
                email_sent_at = state.current_attempt.sent_at
                
                # If cart was updated after email was sent, customer likely returned
                if updated_at > email_sent_at:
                    logger.info("Customer returned to cart after email")
                    return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking cart return: {str(e)}")
        return False


async def check_email_engagement(state: AgentState) -> Dict[str, Any]:
    """
    Check email engagement metrics (opens, clicks)
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with engagement metrics
    """
    engagement = {
        "opened": False,
        "clicked": False,
        "bounced": False,
        "opened_at": None,
        "clicked_at": None
    }
    
    try:
        # In a real implementation, this would check SendGrid webhook data
        # or query SendGrid's Event API
        
        # For now, we'll simulate based on time elapsed
        if state.current_attempt and state.current_attempt.sent_at:
            time_elapsed = datetime.now() - state.current_attempt.sent_at
            
            # Simulate realistic engagement rates
            if time_elapsed.total_seconds() > 300:  # 5 minutes
                # Simulate 25% open rate
                import random
                if random.random() < 0.25:
                    engagement["opened"] = True
                    engagement["opened_at"] = state.current_attempt.sent_at + timedelta(minutes=random.randint(5, 60))
                    
                    # If opened, 15% click rate
                    if random.random() < 0.15:
                        engagement["clicked"] = True
                        engagement["clicked_at"] = engagement["opened_at"] + timedelta(minutes=random.randint(1, 30))
        
        return engagement
        
    except Exception as e:
        logger.error(f"Error checking email engagement: {str(e)}")
        return engagement


def monitor_return_activity_mock(state: AgentState) -> Dict[str, Any]:
    """
    Mock version for development and testing
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with mock monitoring results
    """
    logger.info("Mock: Monitoring return activity")
    
    if not state.cart or not state.customer:
        return {"error_message": "Missing cart or customer information"}
    
    # Simulate monitoring results
    import random
    
    # Simulate realistic recovery rates
    returned_to_cart = random.random() < 0.3  # 30% return rate
    checkout_completed = random.random() < 0.15 if returned_to_cart else random.random() < 0.05  # Higher completion if returned
    recovery_successful = checkout_completed or (returned_to_cart and random.random() < 0.5)
    
    # Mock email engagement
    email_engagement = {
        "opened": random.random() < 0.25,  # 25% open rate
        "clicked": False,
        "bounced": False,
        "opened_at": None,
        "clicked_at": None
    }
    
    if email_engagement["opened"]:
        email_engagement["clicked"] = random.random() < 0.15  # 15% click rate if opened
        if email_engagement["clicked"]:
            email_engagement["clicked_at"] = datetime.now()
    
    logger.info(f"Mock monitoring results - Completed: {checkout_completed}, Returned: {returned_to_cart}, Success: {recovery_successful}")
    
    return {
        "returned_to_cart": returned_to_cart,
        "checkout_completed": checkout_completed,
        "recovery_successful": recovery_successful,
        "workflow_completed_at": datetime.now(),
        "config": {
            **state.config,
            "monitoring_completed": True,
            "email_engagement": email_engagement,
            "monitored_at": datetime.now().isoformat(),
            "mock_mode": True
        }
    }

