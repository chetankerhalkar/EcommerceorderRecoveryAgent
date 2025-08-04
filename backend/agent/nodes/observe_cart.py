"""
Cart Observation Node

This node observes Shopify for abandoned carts that have been inactive
for the specified time period (default: 15+ minutes).
"""

import os
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from ..state import AgentState, Cart, CartItem

logger = logging.getLogger(__name__)


async def observe_abandoned_carts(state: AgentState) -> Dict[str, Any]:
    """
    Observe Shopify for abandoned carts
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with cart information if abandoned cart found
    """
    logger.info("Starting abandoned cart observation")
    
    try:
        # Get configuration
        shopify_url = os.getenv("SHOPIFY_SHOP_URL")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        api_version = os.getenv("SHOPIFY_API_VERSION", "2023-04")
        abandonment_minutes = int(os.getenv("CART_ABANDONMENT_MINUTES", "15"))
        
        if not shopify_url or not access_token:
            logger.error("Missing Shopify configuration")
            return {
                "error_message": "Missing Shopify configuration",
                "is_abandoned": False
            }
        
        # Calculate abandonment threshold
        threshold_time = datetime.now() - timedelta(minutes=abandonment_minutes)
        
        # Construct API URL for abandoned checkouts
        api_url = f"https://{shopify_url}/admin/api/{api_version}/checkouts.json"
        
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        params = {
            "status": "abandoned",
            "limit": 50,
            "updated_at_min": threshold_time.isoformat()
        }
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Shopify API error: {response.status_code} - {response.text}")
                return {
                    "error_message": f"Shopify API error: {response.status_code}",
                    "is_abandoned": False
                }
            
            data = response.json()
            checkouts = data.get("checkouts", [])
            
            if not checkouts:
                logger.info("No abandoned carts found")
                return {
                    "is_abandoned": False,
                    "abandonment_minutes": 0
                }
            
            # Process the first abandoned cart found
            checkout = checkouts[0]
            
            # Calculate actual abandonment time
            updated_at = datetime.fromisoformat(checkout["updated_at"].replace("Z", "+00:00"))
            abandonment_time = (datetime.now(updated_at.tzinfo) - updated_at).total_seconds() / 60
            
            # Convert checkout to our cart format
            cart_items = []
            for line_item in checkout.get("line_items", []):
                cart_item = CartItem(
                    id=line_item["id"],
                    variant_id=line_item["variant_id"],
                    title=line_item["title"],
                    quantity=line_item["quantity"],
                    price=str(line_item["price"]),
                    line_price=str(float(line_item["price"]) * line_item["quantity"]),
                    image=line_item.get("image_url"),
                    url=f"/products/{line_item.get('product_handle', '')}",
                    sku=line_item.get("sku"),
                    vendor=line_item.get("vendor")
                )
                cart_items.append(cart_item)
            
            cart = Cart(
                id=str(checkout["id"]),
                token=checkout.get("token", ""),
                line_items=cart_items,
                total_price=int(float(checkout["total_price"]) * 100),  # Convert to cents
                currency=checkout.get("currency", "USD"),
                created_at=checkout["created_at"],
                updated_at=checkout["updated_at"],
                item_count=sum(item.quantity for item in cart_items)
            )
            
            logger.info(f"Found abandoned cart: {cart.id} (abandoned for {abandonment_time:.1f} minutes)")
            
            return {
                "cart": cart,
                "abandonment_minutes": int(abandonment_time),
                "is_abandoned": abandonment_time >= abandonment_minutes,
                "should_send_recovery": abandonment_time >= abandonment_minutes,
                "workflow_started_at": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"Error observing abandoned carts: {str(e)}")
        return {
            "error_message": f"Error observing carts: {str(e)}",
            "is_abandoned": False
        }


def observe_abandoned_carts_mock(state: AgentState) -> Dict[str, Any]:
    """
    Mock version using local test data for development
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with mock cart information
    """
    logger.info("Using mock abandoned cart data")
    
    try:
        import json
        
        # Load mock data
        mock_file = "/home/ubuntu/aick-abandoned-cart-agent/mock_data/cart.json"
        with open(mock_file, 'r') as f:
            mock_data = json.load(f)
        
        # Convert to our format
        cart_items = []
        for item in mock_data["cart"]["line_items"]:
            cart_item = CartItem(
                id=item["id"],
                variant_id=item["variant_id"],
                title=item["title"],
                quantity=item["quantity"],
                price=item["price"],
                line_price=item["line_price"],
                image=item["image"],
                url=item["url"],
                sku=item["sku"],
                vendor=item["vendor"]
            )
            cart_items.append(cart_item)
        
        cart = Cart(
            id=mock_data["cart"]["id"],
            token=mock_data["cart"]["token"],
            line_items=cart_items,
            total_price=mock_data["cart"]["total_price"],
            currency=mock_data["cart"]["currency"],
            created_at=mock_data["cart"]["created_at"],
            updated_at=mock_data["cart"]["updated_at"],
            item_count=mock_data["cart"]["item_count"]
        )
        
        abandonment_minutes = mock_data["abandonment_info"]["minutes_since_last_activity"]
        
        return {
            "cart": cart,
            "abandonment_minutes": abandonment_minutes,
            "is_abandoned": True,
            "should_send_recovery": True,
            "workflow_started_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error loading mock data: {str(e)}")
        return {
            "error_message": f"Error loading mock data: {str(e)}",
            "is_abandoned": False
        }

