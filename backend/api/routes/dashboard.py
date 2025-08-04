"""
Dashboard API Routes

This module provides REST API endpoints for the frontend dashboard
to display cart recovery analytics and management interface.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics model"""
    total_abandoned_carts: int
    recovery_attempts: int
    successful_recoveries: int
    recovery_rate: float
    total_revenue_recovered: float
    email_open_rate: float
    email_click_rate: float


class CartSummary(BaseModel):
    """Cart summary for dashboard display"""
    cart_id: str
    customer_name: str
    customer_email: str
    total_value: float
    currency: str
    abandoned_at: datetime
    recovery_status: str
    email_sent: bool
    email_opened: bool
    email_clicked: bool
    returned_to_cart: bool
    checkout_completed: bool


class RecentActivity(BaseModel):
    """Recent activity item"""
    timestamp: datetime
    activity_type: str
    description: str
    cart_id: str
    customer_email: str


@router.get("/stats")
async def get_dashboard_stats(
    days: int = Query(default=30, description="Number of days to analyze")
) -> DashboardStats:
    """
    Get dashboard statistics
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Dashboard statistics
    """
    logger.info(f"Getting dashboard stats for last {days} days")
    
    try:
        # In a real implementation, this would query a database
        # For now, we'll return mock statistics
        
        # Simulate realistic e-commerce recovery statistics
        total_abandoned = 150
        attempts = 120
        successful = 18
        recovery_rate = (successful / attempts) * 100 if attempts > 0 else 0
        
        stats = DashboardStats(
            total_abandoned_carts=total_abandoned,
            recovery_attempts=attempts,
            successful_recoveries=successful,
            recovery_rate=recovery_rate,
            total_revenue_recovered=2450.75,
            email_open_rate=24.5,
            email_click_rate=8.3
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/carts")
async def get_abandoned_carts(
    limit: int = Query(default=20, description="Number of carts to return"),
    status: str = Query(default="all", description="Filter by status")
) -> List[CartSummary]:
    """
    Get list of abandoned carts
    
    Args:
        limit: Number of carts to return
        status: Filter by status (all, pending, recovered, failed)
        
    Returns:
        List of cart summaries
    """
    logger.info(f"Getting abandoned carts (limit: {limit}, status: {status})")
    
    try:
        # Mock data for demonstration
        carts = []
        
        # Generate mock cart data
        for i in range(min(limit, 10)):
            cart = CartSummary(
                cart_id=f"cart_{i+1}",
                customer_name=f"Customer {i+1}",
                customer_email=f"customer{i+1}@example.com",
                total_value=round(50 + (i * 25.5), 2),
                currency="USD",
                abandoned_at=datetime.now() - timedelta(hours=i+1),
                recovery_status="pending" if i % 3 == 0 else "recovered" if i % 3 == 1 else "failed",
                email_sent=i % 2 == 0,
                email_opened=i % 3 == 0,
                email_clicked=i % 5 == 0,
                returned_to_cart=i % 4 == 0,
                checkout_completed=i % 6 == 0
            )
            carts.append(cart)
        
        # Filter by status if specified
        if status != "all":
            carts = [cart for cart in carts if cart.recovery_status == status]
        
        return carts
        
    except Exception as e:
        logger.error(f"Failed to get abandoned carts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(default=10, description="Number of activities to return")
) -> List[RecentActivity]:
    """
    Get recent recovery activity
    
    Args:
        limit: Number of activities to return
        
    Returns:
        List of recent activities
    """
    logger.info(f"Getting recent activity (limit: {limit})")
    
    try:
        activities = []
        
        # Generate mock activity data
        activity_types = [
            ("cart_abandoned", "Cart abandoned"),
            ("email_sent", "Recovery email sent"),
            ("email_opened", "Recovery email opened"),
            ("email_clicked", "Recovery email clicked"),
            ("cart_returned", "Customer returned to cart"),
            ("checkout_completed", "Checkout completed")
        ]
        
        for i in range(min(limit, 15)):
            activity_type, description = activity_types[i % len(activity_types)]
            
            activity = RecentActivity(
                timestamp=datetime.now() - timedelta(minutes=i*15),
                activity_type=activity_type,
                description=f"{description} for cart_{i+1}",
                cart_id=f"cart_{i+1}",
                customer_email=f"customer{i+1}@example.com"
            )
            activities.append(activity)
        
        return activities
        
    except Exception as e:
        logger.error(f"Failed to get recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cart/{cart_id}")
async def get_cart_details(cart_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific cart
    
    Args:
        cart_id: Cart identifier
        
    Returns:
        Detailed cart information
    """
    logger.info(f"Getting details for cart: {cart_id}")
    
    try:
        # In a real implementation, this would query the database
        # For now, return mock data based on the cart_id
        
        if cart_id == "mock_cart":
            # Return actual mock data
            import json
            mock_file = r"C:\AICK\EcommerceorderRecoveryAgent\mock_data\cart.json"
            with open(mock_file, 'r') as f:
                mock_data = json.load(f)
            return mock_data
        
        # Generate mock cart details
        cart_details = {
            "cart": {
                "id": cart_id,
                "token": f"token_{cart_id}",
                "line_items": [
                    {
                        "id": 1,
                        "title": "Premium Wireless Headphones",
                        "quantity": 1,
                        "price": "199.99",
                        "image": "https://via.placeholder.com/300x300/f08b55/ffffff?text=Headphones",
                        "vendor": "TechAudio"
                    }
                ],
                "total_price": 19999,
                "currency": "USD",
                "created_at": "2024-01-15T10:30:00-05:00",
                "updated_at": "2024-01-15T10:45:00-05:00",
                "item_count": 1
            },
            "customer": {
                "id": 1,
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "orders_count": 3,
                "total_spent": "450.00"
            },
            "recovery_attempts": [],
            "abandonment_info": {
                "abandoned_at": "2024-01-15T11:00:00-05:00",
                "minutes_since_last_activity": 15,
                "recovery_attempts": 0
            }
        }
        
        return cart_details
        
    except Exception as e:
        logger.error(f"Failed to get cart details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cart/{cart_id}/recover")
async def trigger_cart_recovery(cart_id: str) -> Dict[str, Any]:
    """
    Manually trigger recovery for a specific cart
    
    Args:
        cart_id: Cart identifier
        
    Returns:
        Recovery trigger result
    """
    logger.info(f"Manually triggering recovery for cart: {cart_id}")
    
    try:
        # Get cart details
        cart_details = await get_cart_details(cart_id)
        
        # Trigger recovery using the agent
        from ...agent import AbandonedCartRecoveryAgent
        
        agent = AbandonedCartRecoveryAgent(use_mock=True)
        result = await agent.run_single_cart_recovery(
            cart_data=cart_details["cart"],
            customer_data=cart_details["customer"]
        )
        
        return {
            "success": True,
            "message": f"Recovery triggered for cart {cart_id}",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger cart recovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/recovery-rate")
async def get_recovery_rate_analytics(
    days: int = Query(default=30, description="Number of days to analyze")
) -> Dict[str, Any]:
    """
    Get recovery rate analytics over time
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Recovery rate analytics
    """
    logger.info(f"Getting recovery rate analytics for last {days} days")
    
    try:
        # Generate mock analytics data
        analytics = {
            "period_days": days,
            "daily_stats": [],
            "summary": {
                "average_recovery_rate": 15.2,
                "best_day_rate": 22.5,
                "worst_day_rate": 8.1,
                "trend": "improving"
            }
        }
        
        # Generate daily data
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            abandoned = 5 + (i % 8)
            recovered = max(1, int(abandoned * (0.1 + (i % 3) * 0.05)))
            
            daily_stat = {
                "date": date.strftime("%Y-%m-%d"),
                "abandoned_carts": abandoned,
                "recovered_carts": recovered,
                "recovery_rate": (recovered / abandoned) * 100 if abandoned > 0 else 0
            }
            analytics["daily_stats"].append(daily_stat)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get recovery rate analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

