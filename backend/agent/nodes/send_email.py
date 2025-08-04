"""
Email Sending Node

This node sends recovery emails using SendGrid API and tracks
the email status for monitoring purposes.
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict, Any
import logging
from datetime import datetime

from ..state import AgentState, EmailStatus, RecoveryAttempt

logger = logging.getLogger(__name__)


async def send_recovery_email(state: AgentState) -> Dict[str, Any]:
    """
    Send recovery email using SendGrid
    
    Args:
        state: Current agent state with message content
        
    Returns:
        Updated state with email sending status
    """
    logger.info(f"Sending recovery email to {state.customer.email if state.customer else 'unknown'}")
    
    if not state.customer or not state.email_html_content or not state.email_subject:
        return {"error_message": "Missing customer, subject, or email content"}
    
    try:
        # Get SendGrid configuration
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@aickstudio.com")
        from_name = os.getenv("SENDGRID_FROM_NAME", "AICK Studio")
        
        if not api_key:
            logger.error("Missing SendGrid API key")
            return {"error_message": "Missing SendGrid configuration"}
        
        # Create SendGrid client
        sg = SendGridAPIClient(api_key=api_key)
        
        # Prepare email
        from_email_obj = Email(from_email, from_name)
        to_email = To(state.customer.email)
        subject = state.email_subject
        
        # Create both HTML and plain text versions
        html_content = Content("text/html", state.email_html_content)
        
        # Create plain text version from HTML (simplified)
        plain_text = create_plain_text_version(state.recovery_message or "")
        text_content = Content("text/plain", plain_text)
        
        # Build the email
        mail = Mail(
            from_email=from_email_obj,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )
        
        # Add tracking settings
        mail.tracking_settings = {
            "click_tracking": {"enable": True},
            "open_tracking": {"enable": True},
            "subscription_tracking": {"enable": False}
        }
        
        # Add custom headers for tracking
        mail.custom_args = {
            "cart_id": state.cart.id if state.cart else "",
            "customer_id": str(state.customer.id),
            "recovery_attempt": str(len(state.recovery_attempts) + 1)
        }
        
        # Send the email
        response = sg.send(mail)
        
        # Create email status
        email_status = EmailStatus(
            sent=True,
            sent_at=datetime.now(),
            opened=False,
            clicked=False,
            bounced=False
        )
        
        # Create recovery attempt record
        recovery_attempt = RecoveryAttempt(
            attempt_number=len(state.recovery_attempts) + 1,
            email_subject=subject,
            email_content=state.email_html_content,
            sent_at=datetime.now(),
            status=email_status
        )
        
        logger.info(f"Email sent successfully to {state.customer.email}. Status: {response.status_code}")
        
        return {
            "current_attempt": recovery_attempt,
            "recovery_attempts": state.recovery_attempts + [recovery_attempt],
            "config": {
                **state.config,
                "email_sent": True,
                "sendgrid_message_id": response.headers.get("X-Message-Id"),
                "email_sent_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error sending recovery email: {str(e)}")
        
        # Create failed email status
        email_status = EmailStatus(
            sent=False,
            sent_at=datetime.now(),
            error_message=str(e)
        )
        
        recovery_attempt = RecoveryAttempt(
            attempt_number=len(state.recovery_attempts) + 1,
            email_subject=state.email_subject,
            email_content=state.email_html_content,
            sent_at=datetime.now(),
            status=email_status
        )
        
        return {
            "current_attempt": recovery_attempt,
            "recovery_attempts": state.recovery_attempts + [recovery_attempt],
            "error_message": f"Error sending email: {str(e)}"
        }


def create_plain_text_version(html_content: str) -> str:
    """
    Create a plain text version of the email content
    
    Args:
        html_content: HTML email content
        
    Returns:
        Plain text version
    """
    # Simple HTML to text conversion
    import re
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add some basic formatting
    text = text.replace('Hi ', '\nHi ')
    text = text.replace('. ', '.\n\n')
    
    return text


def send_recovery_email_mock(state: AgentState) -> Dict[str, Any]:
    """
    Mock version for development and testing
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with mock email sending status
    """
    logger.info(f"Mock: Sending recovery email to {state.customer.email if state.customer else 'unknown'}")
    
    if not state.customer or not state.email_html_content or not state.email_subject:
        return {"error_message": "Missing customer, subject, or email content"}
    
    # Simulate successful email sending
    email_status = EmailStatus(
        sent=True,
        sent_at=datetime.now(),
        opened=False,
        clicked=False,
        bounced=False
    )
    
    recovery_attempt = RecoveryAttempt(
        attempt_number=len(state.recovery_attempts) + 1,
        email_subject=state.email_subject,
        email_content=state.email_html_content,
        sent_at=datetime.now(),
        status=email_status
    )
    
    logger.info(f"Mock: Email 'sent' successfully to {state.customer.email}")
    
    return {
        "current_attempt": recovery_attempt,
        "recovery_attempts": state.recovery_attempts + [recovery_attempt],
        "config": {
            **state.config,
            "email_sent": True,
            "mock_mode": True,
            "sendgrid_message_id": "mock_message_id_123",
            "email_sent_at": datetime.now().isoformat()
        }
    }


def send_test_email(to_email: str, subject: str = "Don't miss out, chetan kerhalkar! Your cart is waiting") -> bool:
    import os
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content

    try:
        api_key = os.getenv("SENDGRID_API_KEY", "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")
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@aickstudio.ai")
        from_name = os.getenv("SENDGRID_FROM_NAME", "AICK Studio")
        print(api_key);      
        if not api_key:
            logger.error("Missing SendGrid API key")
            return False

        sg = SendGridAPIClient(api_key=api_key)

        html_content = """
        <html>
        <body>
            <h2>Don't miss out, chetan kerhalkar! Your cart is waiting</h2>
            <p>We noticed you left some amazing items in your cart, and we wanted to make sure you didn't miss out!</p>
            <p>Your selected items represent the perfect blend of innovation and quality that AICK Studio is known for.
These premium products are designed to enhance your tech experience and deliver exceptional value.</p>
<p>Complete your purchase now and join thousands of satisfied customers who trust AICK Studio for their technology needs.</p>
            <br>
            <p>Regards,<br>AICK Studio</p>
        </body>
        </html>
        """

        mail = Mail(
            from_email=Email(from_email, from_name),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        response = sg.send(mail)
        print(f"SendGrid 403 Response: {response.status_code}, {response.body}")
        # 🔍 Log everything
        logger.info(f"SendGrid status: {response.status_code}")
        logger.info(f"SendGrid body: {response.body}")
        logger.info(f"SendGrid headers: {response.headers}")

        # ✅ Consider 2xx as success
        if 200 <= response.status_code < 300:
            return True
        else:
            logger.error(f"SendGrid send failed: {response.status_code} - {response.body}")
            return False

    except Exception as e:
        logger.error(f"Exception while sending email: {str(e)}")
        return False

