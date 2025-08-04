"""
Cart Details Retrieval Node

This node retrieves detailed cart and customer information from Shopify
using the Admin API.
"""

import os
import httpx
from typing import Dict, Any
import logging

from ..state import AgentState, Customer

logger = logging.getLogger(__name__)


async def retrieve_cart_details(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve detailed cart and customer information from Shopify
    
    Args:
        state: Current agent state with cart information
        
    Returns:
        Updated state with customer details
    """
    logger.info(f"Retrieving details for cart: {state.cart.id if state.cart else 'None'}")
    
    if not state.cart:
        return {"error_message": "No cart information available"}
    
    try:
        # Get configuration
        shopify_url = os.getenv("SHOPIFY_SHOP_URL")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        api_version = os.getenv("SHOPIFY_API_VERSION", "2023-04")
        
        if not shopify_url or not access_token:
            logger.error("Missing Shopify configuration")
            return {"error_message": "Missing Shopify configuration"}
        
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        # Get checkout details to find customer ID
        checkout_url = f"https://{shopify_url}/admin/api/{api_version}/checkouts/{state.cart.id}.json"
        
        async with httpx.AsyncClient() as client:
            # Retrieve checkout details
            checkout_response = await client.get(checkout_url, headers=headers)
            
            if checkout_response.status_code != 200:
                logger.error(f"Failed to retrieve checkout: {checkout_response.status_code}")
                return {"error_message": f"Failed to retrieve checkout: {checkout_response.status_code}"}
            
            checkout_data = checkout_response.json()
            checkout = checkout_data.get("checkout", {})
            
            customer_id = checkout.get("customer_id")
            customer_email = checkout.get("email")
            
            if not customer_id and not customer_email:
                logger.warning("No customer information found in checkout")
                return {"error_message": "No customer information available"}
            
            # Retrieve customer details if customer ID is available
            if customer_id:
                customer_url = f"https://{shopify_url}/admin/api/{api_version}/customers/{customer_id}.json"
                customer_response = await client.get(customer_url, headers=headers)
                
                if customer_response.status_code == 200:
                    customer_data = customer_response.json()
                    customer_info = customer_data.get("customer", {})
                    
                    customer = Customer(
                        id=customer_info["id"],
                        email=customer_info["email"],
                        first_name=customer_info.get("first_name"),
                        last_name=customer_info.get("last_name"),
                        phone=customer_info.get("phone"),
                        orders_count=customer_info.get("orders_count", 0),
                        total_spent=customer_info.get("total_spent", "0.00"),
                        accepts_marketing=customer_info.get("accepts_marketing", True),
                        tags=customer_info.get("tags")
                    )
                    
                    logger.info(f"Retrieved customer details: {customer.email}")
                    return {"customer": customer}
            
            # Fallback: create customer object from checkout email
            if customer_email:
                customer = Customer(
                    id=0,  # Unknown customer ID
                    email=customer_email,
                    first_name=checkout.get("billing_address", {}).get("first_name"),
                    last_name=checkout.get("billing_address", {}).get("last_name"),
                    phone=checkout.get("billing_address", {}).get("phone"),
                    orders_count=0,
                    total_spent="0.00",
                    accepts_marketing=True,
                    tags=""
                )
                
                logger.info(f"Created customer from checkout email: {customer.email}")
                return {"customer": customer}
            
            return {"error_message": "Unable to retrieve customer information"}
            
    except Exception as e:
        logger.error(f"Error retrieving cart details: {str(e)}")
        return {"error_message": f"Error retrieving details: {str(e)}"}


def retrieve_cart_details_mock(state: AgentState) -> Dict[str, Any]:
    """
    Mock version using local test data for development
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with mock customer information
    """
    logger.info("Using mock customer data")
    
    try:
        import json
        
        # Load mock data
        mock_file = r"C:\AICK\EcommerceorderRecoveryAgent\mock_data\cart.json"
        with open(mock_file, 'r') as f:
            mock_data = json.load(f)
        
        # Convert to our format
        customer_data = mock_data["customer"]
        customer = Customer(
            id=customer_data["id"],
            email=customer_data["email"],
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            phone=customer_data["phone"],
            orders_count=customer_data["orders_count"],
            total_spent=customer_data["total_spent"],
            accepts_marketing=customer_data["accepts_marketing"],
            tags=customer_data["tags"]
        )
        
        logger.info(f"Loaded mock customer: {customer.email}")
        return {"customer": customer}
        
    except Exception as e:
        logger.error(f"Error loading mock customer data: {str(e)}")
        return {"error_message": f"Error loading mock data: {str(e)}"}

