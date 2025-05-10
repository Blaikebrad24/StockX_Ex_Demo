import requests 
import os 
from typing import Optional, Dict, Any
import json 
import logging 


logger = logging.getLogger(__name__)

class ClerkService:
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.clerk.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def find_user_by_email(self, email: str) -> Optional[str]:
        """Find a user by email in Clerk"""
        try:
            response = requests.get(
                f"{self.base_url}/users",
                headers=self.headers,
                params={"email_address": email}
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    def create_clerk_user(self, email: str, first_name: str, last_name: str) -> Optional[str]:
        """Create a new user in Clerk"""
        try:
            payload = {
                "email_addresses": [{"email": email}],
                "first_name": first_name,
                "last_name": last_name,
                "password_enabled": True
            }
            
            response = requests.post(
                f"{self.base_url}/users",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return data["id"]
        except Exception as e:
            logger.error(f"Error creating Clerk user: {e}")
            return None
        
        
    def send_password_reset_email(self, email: str, user_id: str) -> bool:
        """Send a password reset email to a user"""
        try:
            payload = {
                "email_address_id": email,
                "user_id": user_id
            }
            
            response = requests.post(
                f"{self.base_url}/users/{user_id}/password_reset",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending password reset: {e}")
            return False
    
    
    def create_magic_link(self, email: str, redirect_url: str) -> Optional[str]:
        """Create a magic link for a user"""
        try:
            payload = {
                "email_address": email,
                "redirect_url": redirect_url
            }
            
            response = requests.post(
                f"{self.base_url}/sign_in_tokens/email",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("id")
        except Exception as e:
            logger.error(f"Error creating magic link: {e}")
            return None