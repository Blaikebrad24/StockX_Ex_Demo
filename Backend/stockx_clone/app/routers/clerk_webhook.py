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
from dotenv import load_dotenv
import os 
from svix.webhooks import Webhook, WebhookVerificationError
from app.database import get_db
from app.models.users import User, RoleEnum, UserRole
from app.schemas.user_schema import UserResponse, ClerkUserStatusResponse, SendMagicLinkRequest
from app.service.clerk_service import ClerkService
from app.service.cache_service import CacheService

# Initialize services
from app.dependencies import get_clerk_service, get_cache_service

router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"]
)

load_dotenv()
logger = logging.getLogger(__name__)



def verify_clerk_webhook_with_svix(payload: bytes, headers: dict):
    """
    Verify Clerk webhook using the official Svix library
    
    Args:
        payload: Raw webhook payload as bytes
        headers: Request headers containing svix-* headers
    
    Returns:
        dict: Parsed webhook data if verification succeeds
        
    Raises:
        HTTPException: If verification fails
    """
    webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
    
    if not webhook_secret:
        logger.error("CLERK_WEBHOOK_SECRET environment variable not set")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Create Svix webhook instance
    wh = Webhook(webhook_secret)
    
    try:
        # Verify and parse the webhook
        # The verify method returns the parsed JSON payload
        payload_data = wh.verify(payload, headers)
        logger.info("Webhook verification successful")
        return payload_data
        
    except WebhookVerificationError as e:
        logger.error(f"Webhook verification failed: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Webhook verification failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during webhook verification: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error verifying webhook: {str(e)}"
        )
    

def handle_user_created(db: Session, data: Dict[Any, Any], cache_service: CacheService):
    """Handle user.created event from Clerk"""
    logger.info(f"Handling user creation: {data}")
    
    try:
        clerk_id = data.get("id")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if existing_user:
            logger.info(f"User already exists with clerkId: {clerk_id}")
            return existing_user.id
        
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
        
        # Save user first
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create and add the FREE_USER role as a UserRole object
        user_role = UserRole(
            user_id=user.id,
            role=RoleEnum.FREE_USER.value  # Use .value to get the string
        )
        db.add(user_role)
        db.commit()
        db.refresh(user)  # Refresh to load the new relationship
        
        # Cache user data
        user_data = {
            "id": str(user.id),
            "clerk_id": user.clerk_id,
            "email": user.email,
            "name": user.name,
            "roles": [role.role for role in user.roles]  # Get role strings from UserRole objects
        }
        cache_service.user_cache(clerk_id, user_data)
        
        logger.info(f"Successfully created and cached user with ID: {user.id}")
        return user.id
    
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

def handle_user_deleted(db: Session, data: Dict[Any, Any], cache_service: CacheService):
    """Handle user.deleted event from Clerk"""
    clerk_id = data.get("id")
    logger.info(f"Handling user deletion for ID: {clerk_id}")
    
    try:
        # Find the user in the database
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if user:
            # Delete user roles first (foreign key constraint)
            for role in user.roles:
                db.delete(role)
            
            # Delete the user
            db.delete(user)
            db.commit()
            
            # Remove from cache
            cache_service.invalidate_user_cache(clerk_id)
            logger.info(f"User deleted successfully: {clerk_id}")
            return True
        else:
            logger.warning(f"User not found for deletion: {clerk_id}")
            return False
    
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.rollback()
        raise

def handle_session_ended(db: Session, data: Dict[Any, Any], cache_service: CacheService):
    """Handle session.ended event from Clerk"""
    user_id = data.get("user_id")
    logger.info(f"Handling session end for user ID: {user_id}")
    
    try:
        # Find user and potentially clear some session-specific cache
        user = db.query(User).filter(User.clerk_id == user_id).first()
        if user:
            # You could update last_seen or other session-related fields here
            logger.info(f"Session ended for user: {user_id}")
            return user.id
        else:
            logger.warning(f"User not found for session end: {user_id}")
            return None
    
    except Exception as e:
        logger.error(f"Error handling session end: {str(e)}")
        raise


@router.post("/clerk")
async def handle_clerk_webhook(request: Request,db: Session = Depends(get_db),clerk_service: ClerkService = Depends(get_clerk_service),cache_service: CacheService = Depends(get_cache_service)):
    """Handle Clerk webhook events using Svix verification"""
    
    # Get raw payload as bytes (important for signature verification)
    payload = await request.body()
    
    # Convert headers to dict for Svix
    headers = dict(request.headers)
    
    # Log incoming webhook info
    logger.info(f"Received webhook from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Headers: svix-id={headers.get('svix-id')}, svix-timestamp={headers.get('svix-timestamp')}")
    logger.info(f"Payload size: {len(payload)} bytes")
    
    try:
        # Verify webhook and get parsed data using Svix
        webhook_data = verify_clerk_webhook_with_svix(payload, headers)
        
        # Extract event information
        event_type = webhook_data.get("type")
        event_data = webhook_data.get("data", {})
        object_id = webhook_data.get("object", "unknown")
        
        logger.info(f"Processing event: {event_type} for object: {object_id}")
        
        # Handle different event types
        if event_type == "user.created":
            result = handle_user_created(db, event_data, cache_service)
            logger.info(f"User created successfully: {result}")
            
        elif event_type == "user.updated":
            result = handle_user_updated(db, event_data, cache_service)
            logger.info(f"User updated successfully: {result}")
            
        elif event_type == "user.deleted":
            result = handle_user_deleted(db, event_data, cache_service)
            logger.info(f"User deleted successfully: {result}")
            
        elif event_type == "session.created":
            result = handle_session_created(db, event_data, cache_service)
            logger.info(f"Session created successfully: {result}")
            
        elif event_type == "session.ended":
            result = handle_session_ended(db, event_data, cache_service)
            logger.info(f"Session ended successfully: {result}")
            
        else:
            logger.info(f"Unhandled event type: {event_type}")
            # Still return success for unknown events
        
        return {
            "status": "success", 
            "message": f"Successfully processed {event_type} event",
            "event_id": headers.get('svix-id'),
            "timestamp": headers.get('svix-timestamp')
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions (these have proper status codes)
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal error processing webhook: {str(e)}"
        )


@router.get("/user-status", response_model=ClerkUserStatusResponse)
async def get_user_status(email: str, db: Session = Depends(get_db),clerk_service: ClerkService = Depends(get_clerk_service)):
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
async def send_magic_link(request: SendMagicLinkRequest,clerk_service: ClerkService = Depends(get_clerk_service)):
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