from fastapi import APIRouter, Depends, Request, HTTPException, Header
from typing import Optional, Dict, Any, List
import json
import hmac
import hashlib
import time
from sqlalchemy.orm import Session
import logging
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import get_db
from app.models.users import User, RoleEnum
from app.schemas.user_schema import UserResponse, ClerkUserStatusResponse, SendMagicLinkRequest
from app.service.clerk_service import ClerkService
from app.service.cache_service import CacheService

# Initialize services
from app.dependencies import get_clerk_service, get_cache_service

router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"]
)

logger = logging.getLogger(__name__)

def verify_clerk_webhook(
    payload: str,
    svix_id: str = Header(...),
    svix_timestamp: str = Header(...),
    svix_signature: str = Header(...),
    clerk_webhook_secret: str = Depends(lambda: get_clerk_service().webhook_secret)
):
    """Verify the Clerk webhook signature"""
    if not clerk_webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Convert timestamp to int
    timestamp = int(svix_timestamp)
    
    # Verify timestamp (within 5 minutes)
    now = int(time.time())
    if abs(now - timestamp) > 300:
        raise HTTPException(status_code=401, detail="Webhook timestamp too old")
    
    # Create signature
    to_sign = f"{svix_id}.{svix_timestamp}.{payload}"
    signature = hmac.new(
        clerk_webhook_secret.encode(), 
        to_sign.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    # Verify signature
    if not hmac.compare_digest(signature, svix_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    return True

@router.post("/clerk")
async def handle_clerk_webhook(
    request: Request,
    db: Session = Depends(get_db),
    clerk_service: ClerkService = Depends(get_clerk_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Handle Clerk webhook events"""
    # Get request data
    payload = await request.body()
    payload_str = payload.decode()
    
    # Headers for verification
    svix_id = request.headers.get("svix-id")
    svix_signature = request.headers.get("svix-signature")
    svix_timestamp = request.headers.get("svix-timestamp")
    
    # Log webhook info
    logger.info(f"Received webhook with ID: {svix_id}")
    logger.info(f"Signature: {svix_signature}")
    logger.info(f"Timestamp: {svix_timestamp}")
    logger.info(f"Payload length: {len(payload_str)}")
    
    try:
        # Verify webhook
        verify_clerk_webhook(payload_str, svix_id, svix_timestamp, svix_signature)
        
        # Parse webhook data
        webhook_data = json.loads(payload_str)
        event_type = webhook_data.get("type")
        data = webhook_data.get("data", {})
        
        logger.info(f"Processing event type: {event_type}")
        
        # Handle different event types
        if event_type == "user.created":
            handle_user_created(db, data, cache_service)
        elif event_type == "user.updated":
            handle_user_updated(db, data, cache_service)
        elif event_type == "session.created":
            handle_session_created(db, data, cache_service)
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success"}
    
    except HTTPException as e:
        logger.error(f"Webhook verification failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

def handle_user_created(db: Session, data: Dict[Any, Any], cache_service: CacheService):
    """Handle user.created event from Clerk"""
    logger.info(f"Handling user creation: {data}")
    
    try:
        clerk_id = data.get("id")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if existing_user:
            logger.info(f"User already exists with clerkId: {clerk_id}")
            return
        
        # Create new user
        user = User(
            clerk_id=clerk_id,
            version=0
        )
        
        # Extract email
        if data.get("email_addresses") and len(data["email_addresses"]) > 0:
            user.email = data["email_addresses"][0]["email_address"]
        
        # Extract name
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        user.name = f"{first_name} {last_name}".strip()
        
        # Set default role
        user.roles = [Role.FREE_USER]
        
        # Save to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Cache user data
        user_data = {
            "id": str(user.id),
            "clerk_id": user.clerk_id,
            "email": user.email,
            "name": user.name,
            "roles": [role.value for role in user.roles]
        }
        cache_service.user_cache(clerk_id, user_data)
        
        logger.info(f"Successfully created and cached user with ID: {user.id}")
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise

def handle_user_updated(db: Session, data: Dict[Any, Any], cache_service: CacheService):
    """Handle user.updated event from Clerk"""
    clerk_id = data.get("id")
    logger.info(f"Handling clerk User update for ID: {clerk_id}")
    
    try:
        # Find the user in the database
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if not user:
            logger.error(f"User not found with clerk ID: {clerk_id}")
            return
        
        # Update user fields
        if data.get("email_addresses") and len(data["email_addresses"]) > 0:
            user.email = data["email_addresses"][0]["email_address"]
        
        if data.get("first_name") is not None or data.get("last_name") is not None:
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            user.name = f"{first_name} {last_name}".strip()
        
        # Check for paid status
        if data.get("paid_user") and data["paid_user"]:
            # Check if user already has PAID_USER role
            existing_roles = [role.role for role in user.roles]
            
            if RoleEnum.FREE_USER.value in existing_roles:
                # Find and remove the FREE_USER role
                for role in user.roles:
                    if role.role == RoleEnum.FREE_USER.value:
                        db.delete(role)
            
            if RoleEnum.PAID_USER.value not in existing_roles:
                # Add the PAID_USER role
                new_role = UserRole(
                    user_id=user.id,
                    role=RoleEnum.PAID_USER.value
                )
                db.add(new_role)
        
        # Save changes
        db.commit()
        db.refresh(user)
        
        # Update cache
        user_data = {
            "id": str(user.id),
            "clerk_id": user.clerk_id,
            "email": user.email,
            "name": user.name,
            "roles": [role.role for role in user.roles]
        }
        cache_service.user_cache(clerk_id, user_data)
        
        logger.info(f"User updated successfully: {user.id}")
    
    except Exception as e:
        logger.error(f"Error updating User: {str(e)}")
        db.rollback()
        raise

def handle_session_created(db: Session, data: Dict[Any, Any], cache_service: CacheService):
    """Handle session.created event from Clerk"""
    user_id = data.get("user_id")
    logger.info(f"Handling session creation for user ID: {user_id}")
    
    try:
        # Find user
        user = db.query(User).filter(User.clerk_id == user_id).first()
        if user:
            # Refresh cache
            user_data = {
                "id": str(user.id),
                "clerk_id": user.clerk_id,
                "email": user.email,
                "name": user.name,
                "roles": [role.value for role in user.roles]
            }
            cache_service.user_cache(user_id, user_data)
            logger.info(f"Refreshed cache for user: {user_id}")
    
    except Exception as e:
        logger.error(f"Error handling session creation: {str(e)}")
        raise

@router.get("/user-status", response_model=ClerkUserStatusResponse)
async def get_user_status(
    email: str,
    db: Session = Depends(get_db),
    clerk_service: ClerkService = Depends(get_clerk_service)
):
    """Check if a user exists in the system and Clerk"""
    logger.info(f"Checking user status for email: {email}")
    
    try:
        # Check database
        db_user = db.query(User).filter(User.email == email).first()
        
        # Check Clerk
        clerk_user_id = clerk_service.find_user_by_email(email)
        
        response = ClerkUserStatusResponse(
            exists_in_database=db_user is not None,
            exists_in_clerk=clerk_user_id is not None,
            clerk_id=clerk_user_id,
            email=email
        )
        
        if db_user:
            response.user_id = str(db_user.id)
            response.name = db_user.name
            
            # If user exists in database but not in Clerk, create Clerk account
            if not clerk_user_id and (not db_user.clerk_id or not db_user.clerk_id.strip()):
                try:
                    # Parse name
                    first_name = db_user.name
                    last_name = ""
                    
                    if " " in db_user.name:
                        name_parts = db_user.name.split(" ", 1)
                        first_name = name_parts[0]
                        last_name = name_parts[1]
                    
                    # Create Clerk user
                    new_clerk_id = clerk_service.create_clerk_user(
                        email, 
                        first_name, 
                        last_name
                    )
                    
                    if new_clerk_id:
                        db_user.clerk_id = new_clerk_id
                        db.commit()
                        
                        response.clerk_id = new_clerk_id
                        response.exists_in_clerk = True
                        response.newly_created = True
                        
                        # Send password reset
                        clerk_service.send_password_reset_email(email, new_clerk_id)
                
                except Exception as e:
                    logger.error(f"Error creating Clerk user: {str(e)}")
            
            # Check for Clerk ID mismatch
            if clerk_user_id and db_user.clerk_id and db_user.clerk_id != clerk_user_id:
                logger.warning(f"Clerk ID mismatch for user {db_user.id}: DB has {db_user.clerk_id}, API found {clerk_user_id}")
                
                # Update Clerk ID
                db_user.clerk_id = clerk_user_id
                db.commit()
                response.clerk_id_updated = True
        
        return response
    
    except Exception as e:
        logger.error(f"Error checking user status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking user status: {str(e)}")

@router.post("/send-magic-link")
async def send_magic_link(
    request: SendMagicLinkRequest,
    clerk_service: ClerkService = Depends(get_clerk_service)
):
    """Send a magic link email to a user"""
    logger.info(f"Sending magic link to: {request.email}")
    
    try:
        magic_link = clerk_service.create_magic_link(
            request.email,
            request.redirect_url
        )
        
        if magic_link:
            return {"success": True, "message": "Magic link sent successfully"}
        else:
            return {"success": False, "message": "Failed to create magic link"}
    
    except Exception as e:
        logger.error(f"Error sending magic link: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending magic link: {str(e)}")