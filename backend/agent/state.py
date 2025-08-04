"""
Agent State Definition for Abandoned Cart Recovery

This module defines the state structure that flows through the LangGraph workflow.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CartItem(BaseModel):
    """Individual cart item structure"""
    id: int
    variant_id: int
    title: str
    quantity: int
    price: str
    line_price: str
    image: Optional[str] = None
    url: Optional[str] = None
    sku: Optional[str] = None
    vendor: Optional[str] = None


class Customer(BaseModel):
    """Customer information structure"""
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    orders_count: int = 0
    total_spent: str = "0.00"
    accepts_marketing: bool = True
    tags: Optional[str] = None


class Cart(BaseModel):
    """Shopping cart structure"""
    id: str
    token: str
    line_items: List[CartItem]
    total_price: int
    currency: str = "USD"
    created_at: str
    updated_at: str
    item_count: int


class EmailStatus(BaseModel):
    """Email tracking status"""
    sent: bool = False
    sent_at: Optional[datetime] = None
    opened: bool = False
    opened_at: Optional[datetime] = None
    clicked: bool = False
    clicked_at: Optional[datetime] = None
    bounced: bool = False
    error_message: Optional[str] = None


class RecoveryAttempt(BaseModel):
    """Recovery attempt tracking"""
    attempt_number: int
    email_subject: str
    email_content: str
    sent_at: datetime
    status: EmailStatus


class AgentState(BaseModel):
    """
    Main state object that flows through the LangGraph workflow
    """
    # Input data
    cart: Optional[Cart] = None
    customer: Optional[Customer] = None
    
    # Processing state
    abandonment_minutes: int = 0
    is_abandoned: bool = False
    should_send_recovery: bool = False
    
    # Generated content
    recovery_message: Optional[str] = None
    email_subject: Optional[str] = None
    email_html_content: Optional[str] = None
    
    # Tracking
    recovery_attempts: List[RecoveryAttempt] = Field(default_factory=list)
    current_attempt: Optional[RecoveryAttempt] = None
    
    # Monitoring
    returned_to_cart: bool = False
    checkout_completed: bool = False
    recovery_successful: bool = False
    
    # Metadata
    workflow_started_at: Optional[datetime] = None
    workflow_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

