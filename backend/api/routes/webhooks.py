"""
Webhook API Routes

This module handles incoming webhooks from Shopify and SendGrid
for real-time cart and email event processing.
"""

import os
import hmac
import hashlib
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/shopify/cart-update")
async def handle_shopify_cart_webhook(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    x_shopify_topic: str = Header(None)
) -> Dict[str, Any]:
    """
    Handle Shopify cart update webhooks
    
    Args:
        request: FastAPI request object
        x_shopify_hmac_sha256: Shopify HMAC signature
        x_shopify_topic: Shopify webhook topic
        
    Returns:
        Webhook processing result
    """
    logger.info(f"Received Shopify webhook: {x_shopify_topic}")
    
    try:
        # Get request body
        body = await request.body()
        
        # Verify webhook signature
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if webhook_secret and x_shopify_hmac_sha256:
            if not verify_shopify_webhook(body, x_shopify_hmac_sha256, webhook_secret):
                logger.warning("Invalid Shopify webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        import json
        webhook_data = json.loads(body.decode('utf-8'))
        
        # Process different webhook topics
        if x_shopify_topic == "carts/update":
            await process_cart_update(webhook_data)
        elif x_shopify_topic == "checkouts/create":
            await process_checkout_create(webhook_data)
        elif x_shopify_topic == "checkouts/update":
            await process_checkout_update(webhook_data)
        elif x_shopify_topic == "orders/create":
            await process_order_create(webhook_data)
        else:
            logger.info(f"Unhandled webhook topic: {x_shopify_topic}")
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing Shopify webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sendgrid/events")
async def handle_sendgrid_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle SendGrid email event webhooks
    
    Args:
        request: FastAPI request object
        
    Returns:
        Webhook processing result
    """
    logger.info("Received SendGrid webhook")
    
    try:
        # Get request body
        body = await request.body()
        
        # Parse webhook data
        import json
        events = json.loads(body.decode('utf-8'))
        
        # Process each event
        for event in events:
            await process_sendgrid_event(event)
        
        return {"status": "success", "message": f"Processed {len(events)} events"}
        
    except Exception as e:
        logger.error(f"Error processing SendGrid webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def verify_shopify_webhook(body: bytes, signature: str, secret: str) -> bool:
    """
    Verify Shopify webhook signature
    
    Args:
        body: Request body
        signature: Shopify signature header
        secret: Webhook secret
        
    Returns:
        True if signature is valid
    """
    try:
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


async def process_cart_update(cart_data: Dict[str, Any]) -> None:
    """
    Process cart update webhook
    
    Args:
        cart_data: Cart data from webhook
    """
    logger.info(f"Processing cart update: {cart_data.get('id')}")
    
    try:
        # Check if cart is abandoned (no activity for specified time)
        from datetime import datetime, timedelta
        
        updated_at = datetime.fromisoformat(cart_data["updated_at"].replace("Z", "+00:00"))
        abandonment_threshold = datetime.now(updated_at.tzinfo) - timedelta(
            minutes=int(os.getenv("CART_ABANDONMENT_MINUTES", "15"))
        )
        
        if updated_at < abandonment_threshold:
            logger.info(f"Cart {cart_data['id']} is abandoned, triggering recovery")
            
            # Trigger recovery workflow
            from ...agent import AbandonedCartRecoveryAgent
            
            agent = AbandonedCartRecoveryAgent()
            # Note: In a real implementation, you'd extract customer data from the cart
            # and trigger the recovery workflow
            
    except Exception as e:
        logger.error(f"Error processing cart update: {str(e)}")


async def process_checkout_create(checkout_data: Dict[str, Any]) -> None:
    """
    Process checkout creation webhook
    
    Args:
        checkout_data: Checkout data from webhook
    """
    logger.info(f"Processing checkout create: {checkout_data.get('id')}")
    
    # This could be used to start monitoring for abandonment
    # Implementation depends on specific business logic


async def process_checkout_update(checkout_data: Dict[str, Any]) -> None:
    """
    Process checkout update webhook
    
    Args:
        checkout_data: Checkout data from webhook
    """
    logger.info(f"Processing checkout update: {checkout_data.get('id')}")
    
    # Check if customer returned to checkout after recovery email
    # Update recovery tracking accordingly


async def process_order_create(order_data: Dict[str, Any]) -> None:
    """
    Process order creation webhook (successful recovery)
    
    Args:
        order_data: Order data from webhook
    """
    logger.info(f"Processing order create: {order_data.get('id')}")
    
    # Mark any related recovery attempts as successful
    # Update analytics and tracking


async def process_sendgrid_event(event: Dict[str, Any]) -> None:
    """
    Process individual SendGrid event
    
    Args:
        event: SendGrid event data
    """
    event_type = event.get("event")
    logger.info(f"Processing SendGrid event: {event_type}")
    
    try:
        # Extract tracking information
        cart_id = event.get("cart_id")  # From custom args
        customer_id = event.get("customer_id")
        recovery_attempt = event.get("recovery_attempt")
        
        # Process different event types
        if event_type == "delivered":
            await handle_email_delivered(event, cart_id, customer_id)
        elif event_type == "open":
            await handle_email_opened(event, cart_id, customer_id)
        elif event_type == "click":
            await handle_email_clicked(event, cart_id, customer_id)
        elif event_type == "bounce":
            await handle_email_bounced(event, cart_id, customer_id)
        elif event_type == "unsubscribe":
            await handle_email_unsubscribed(event, cart_id, customer_id)
        
    except Exception as e:
        logger.error(f"Error processing SendGrid event: {str(e)}")


async def handle_email_delivered(event: Dict[str, Any], cart_id: str, customer_id: str) -> None:
    """Handle email delivered event"""
    logger.info(f"Email delivered for cart {cart_id}")
    # Update delivery status in database


async def handle_email_opened(event: Dict[str, Any], cart_id: str, customer_id: str) -> None:
    """Handle email opened event"""
    logger.info(f"Email opened for cart {cart_id}")
    # Update open status and timestamp in database


async def handle_email_clicked(event: Dict[str, Any], cart_id: str, customer_id: str) -> None:
    """Handle email clicked event"""
    logger.info(f"Email clicked for cart {cart_id}")
    # Update click status and timestamp in database
    # This is a strong indicator of engagement


async def handle_email_bounced(event: Dict[str, Any], cart_id: str, customer_id: str) -> None:
    """Handle email bounced event"""
    logger.info(f"Email bounced for cart {cart_id}")
    # Mark email as bounced, don't send future emails to this address


async def handle_email_unsubscribed(event: Dict[str, Any], cart_id: str, customer_id: str) -> None:
    """Handle email unsubscribed event"""
    logger.info(f"Email unsubscribed for cart {cart_id}")
    # Mark customer as unsubscribed from marketing emails


# Test webhook endpoints for development
@router.post("/test/shopify")
async def test_shopify_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test endpoint for Shopify webhooks
    
    Args:
        data: Test webhook data
        
    Returns:
        Test result
    """
    logger.info("Processing test Shopify webhook")
    
    try:
        await process_cart_update(data)
        return {"status": "success", "message": "Test webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing test webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/sendgrid")
async def test_sendgrid_webhook(events: list) -> Dict[str, Any]:
    """
    Test endpoint for SendGrid webhooks
    
    Args:
        events: Test event data
        
    Returns:
        Test result
    """
    logger.info("Processing test SendGrid webhook")
    
    try:
        for event in events:
            await process_sendgrid_event(event)
        
        return {"status": "success", "message": f"Processed {len(events)} test events"}
        
    except Exception as e:
        logger.error(f"Error processing test webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

