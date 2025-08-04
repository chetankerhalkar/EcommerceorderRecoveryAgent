"""
Message Planning Node

This node uses OpenAI GPT-4 to generate personalized recovery messages
based on cart contents and customer information.
"""

import os
from openai import AsyncOpenAI
from typing import Dict, Any
import logging
from datetime import datetime

from ..state import AgentState

logger = logging.getLogger(__name__)


async def plan_recovery_message(state: AgentState) -> Dict[str, Any]:
    """
    Generate personalized recovery message using OpenAI GPT-4
    
    Args:
        state: Current agent state with cart and customer information
        
    Returns:
        Updated state with generated message content
    """
    logger.info("Planning recovery message with GPT-4")
    
    if not state.cart or not state.customer:
        return {"error_message": "Missing cart or customer information"}
    
    try:
        # Initialize OpenAI client
        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        
        # Prepare cart items summary
        items_summary = []
        total_value = 0
        
        for item in state.cart.line_items:
            price_float = float(item.price)
            line_total = price_float * item.quantity
            total_value += line_total
            
            items_summary.append({
                "name": item.title,
                "quantity": item.quantity,
                "price": f"${price_float:.2f}",
                "total": f"${line_total:.2f}",
                "vendor": item.vendor
            })
        
        # Customer context
        customer_name = f"{state.customer.first_name or ''} {state.customer.last_name or ''}".strip()
        if not customer_name:
            customer_name = state.customer.email.split('@')[0].title()
        
        is_returning_customer = state.customer.orders_count > 0
        customer_tier = "VIP" if "vip" in (state.customer.tags or "").lower() else "valued"
        
        # Create the prompt for GPT-4
        system_prompt = """You are an expert email marketing specialist for AICK Studio, a premium technology brand. 
        
        Your task is to create compelling, personalized abandoned cart recovery emails that:
        1. Feel personal and genuine, not robotic
        2. Create urgency without being pushy
        3. Highlight the value and benefits of the products
        4. Include a clear call-to-action
        5. Reflect AICK Studio's premium, intelligent brand voice
        
        Brand Voice: Professional yet approachable, innovative, customer-focused, premium quality.
        Brand Colors: Orange (#f08b55), Deep Rust (#a0451a), Purple (#6f4889), Blue (#1844a3), Olive Green (#587834)
        
        Return your response as JSON with these fields:
        - "subject": Email subject line (compelling, under 50 characters)
        - "message": Email body (HTML format, professional design)
        - "tone": Brief description of the tone used
        """
        
        user_prompt = f"""Create an abandoned cart recovery email for:

        Customer: {customer_name} ({state.customer.email})
        Customer Type: {"Returning customer" if is_returning_customer else "New customer"} ({customer_tier})
        Previous Orders: {state.customer.orders_count}
        Cart Abandonment: {state.abandonment_minutes} minutes ago

        Cart Contents:
        {chr(10).join([f"- {item['name']} (Qty: {item['quantity']}) - {item['total']}" for item in items_summary])}
        
        Total Cart Value: ${total_value:.2f}
        
        Make it personal, compelling, and aligned with AICK Studio's premium brand identity."""
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse response
        import json
        message_content = response.choices[0].message.content
        
        try:
            parsed_response = json.loads(message_content)
            email_subject = parsed_response.get("subject", "Complete Your Purchase - AICK Studio")
            email_html = parsed_response.get("message", "")
            tone_used = parsed_response.get("tone", "professional")
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            email_subject = "Complete Your Purchase - AICK Studio"
            email_html = message_content
            tone_used = "professional"
        
        # Enhance HTML with AICK Studio branding
        branded_html = create_branded_email_template(
            email_html, 
            customer_name, 
            items_summary, 
            total_value,
            state.cart.id
        )
        
        logger.info(f"Generated recovery message for {state.customer.email}")
        
        return {
            "email_subject": email_subject,
            "recovery_message": email_html,
            "email_html_content": branded_html,
            "config": {
                **state.config,
                "message_tone": tone_used,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating recovery message: {str(e)}")
        return {"error_message": f"Error generating message: {str(e)}"}


def create_branded_email_template(content: str, customer_name: str, items: list, total: float, cart_id: str) -> str:
    """
    Create a branded HTML email template with AICK Studio styling
    
    Args:
        content: Generated message content
        customer_name: Customer's name
        items: Cart items summary
        total: Total cart value
        cart_id: Cart identifier
        
    Returns:
        Complete HTML email template
    """
    
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                <strong>{item['name']}</strong><br>
                <small>Qty: {item['quantity']} × {item['price']} = {item['total']}</small>
            </td>
        </tr>
        """
    
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Complete Your Purchase - AICK Studio</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #f08b55 0%, #a0451a 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">AICK STUDIO</h1>
                                <p style="color: white; margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">IGNITE INTELLECT, BUILD WITH INTELLIGENCE</p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #333; margin: 0 0 20px 0; font-size: 24px;">Hi {customer_name},</h2>
                                
                                <div style="color: #555; line-height: 1.6; margin-bottom: 30px;">
                                    {content}
                                </div>
                                
                                <!-- Cart Items -->
                                <div style="background-color: #f9f9f9; border-radius: 6px; padding: 20px; margin: 30px 0;">
                                    <h3 style="color: #333; margin: 0 0 15px 0; font-size: 18px;">Your Cart Items:</h3>
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        {items_html}
                                        <tr>
                                            <td style="padding: 15px 10px 0 10px; text-align: right; font-weight: bold; font-size: 18px; color: #f08b55;">
                                                Total: ${total:.2f}
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                
                                <!-- CTA Button -->
                                <div style="text-align: center; margin: 40px 0;">
                                    <a href="https://checkout.example.com/cart/{cart_id}" 
                                       style="background: linear-gradient(135deg, #f08b55 0%, #a0451a 100%); 
                                              color: white; 
                                              text-decoration: none; 
                                              padding: 15px 30px; 
                                              border-radius: 6px; 
                                              font-weight: bold; 
                                              font-size: 16px; 
                                              display: inline-block;">
                                        Complete Your Purchase
                                    </a>
                                </div>
                                
                                <p style="color: #777; font-size: 14px; text-align: center; margin-top: 30px;">
                                    Questions? Reply to this email or contact our support team.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #333; color: white; padding: 20px 30px; text-align: center; border-radius: 0 0 8px 8px;">
                                <p style="margin: 0; font-size: 14px;">
                                    © 2024 AICK Studio. All rights reserved.
                                </p>
                                <p style="margin: 10px 0 0 0; font-size: 12px; opacity: 0.8;">
                                    <a href="#" style="color: #f08b55; text-decoration: none;">Unsubscribe</a> | 
                                    <a href="#" style="color: #f08b55; text-decoration: none;">Privacy Policy</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return template


def plan_recovery_message_mock(state: AgentState) -> Dict[str, Any]:
    """
    Mock version for development and testing
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with mock message content
    """
    logger.info("Using mock message generation")
    
    if not state.cart or not state.customer:
        return {"error_message": "Missing cart or customer information"}
    
    customer_name = f"{state.customer.first_name or ''} {state.customer.last_name or ''}".strip()
    if not customer_name:
        customer_name = state.customer.email.split('@')[0].title()
    
    # Generate mock content
    items_summary = []
    total_value = 0
    
    for item in state.cart.line_items:
        price_float = float(item.price)
        line_total = price_float * item.quantity
        total_value += line_total
        
        items_summary.append({
            "name": item.title,
            "quantity": item.quantity,
            "price": f"${price_float:.2f}",
            "total": f"${line_total:.2f}",
            "vendor": item.vendor
        })
    
    mock_subject = f"Don't miss out, {customer_name}! Your cart is waiting"
    mock_message = f"""
    <p>We noticed you left some amazing items in your cart, and we wanted to make sure you didn't miss out!</p>
    
    <p>Your selected items represent the perfect blend of innovation and quality that AICK Studio is known for. 
    These premium products are designed to enhance your tech experience and deliver exceptional value.</p>
    
    <p>Complete your purchase now and join thousands of satisfied customers who trust AICK Studio for their technology needs.</p>
    """
    
    branded_html = create_branded_email_template(
        mock_message,
        customer_name,
        items_summary,
        total_value,
        state.cart.id
    )
    
    return {
        "email_subject": mock_subject,
        "recovery_message": mock_message,
        "email_html_content": branded_html,
        "config": {
            **state.config,
            "message_tone": "friendly_professional",
            "generated_at": datetime.now().isoformat(),
            "mock_mode": True
        }
    }

