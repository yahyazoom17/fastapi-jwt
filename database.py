import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from fastapi import HTTPException, status
from mongoengine import connect, disconnect
from dotenv import load_dotenv

# Local imports
from models import Users, Contacts
from jwtsign import sign_user

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "contacts_db")
DB_PORT = int(os.getenv("DB_PORT", 5000))

# Create database connection
def get_db_connection():
    """Establish connection to MongoDB"""
    try:
        connect(db=DB_NAME, host=DB_HOST, port=DB_PORT)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(e)}"
        )

# User operations
def saveUserToDB(userdata: Dict[str, str]) -> Dict[str, str]:
    """
    Save a new user to the database
    
    Args:
        userdata: Dictionary containing user data
        
    Returns:
        Dictionary with result message
    """
    try:
        get_db_connection()
        
        # Check if email already exists
        existing_user = Users.objects(email=userdata["email"]).first()
        if existing_user:
            return {"message": "Email already registered!"}
        
        # Create and save new user
        user = Users(
            name=userdata["name"], 
            email=userdata["email"], 
            password=userdata["password"]  # Should be hashed in production
        )
        user.save()
        
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()

def getUserFromDB(userdata: Dict[str, str]) -> Dict[str, Any]:
    """
    Authenticate user and generate token
    
    Args:
        userdata: Dictionary containing login credentials
        
    Returns:
        Dictionary with user name and access token
    """
    try:
        get_db_connection()
        
        # Find user with matching credentials
        user = Users.objects(
            email=userdata["email"], 
            password=userdata["password"]  # Should use secure comparison in production
        ).first()
        
        if user:
            # Generate JWT token
            token = sign_user({"sub": user.name}, timedelta(minutes=30))
            return {
                "name": user.name, 
                "access_token": token, 
                "token_type": "bearer"
            }
        
        return {"message": "Incorrect email or password!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()

# Contact operations
def getUserContacts(username: str) -> Dict[str, Any]:
    """
    Get all contacts for a user
    
    Args:
        username: Username of the contacts owner
        
    Returns:
        Dictionary with contacts list and count
    """
    try:
        get_db_connection()
        
        contacts = []
        user_contacts = Contacts.objects(user=username)
        
        for contact in user_contacts:
            contacts.append({
                "id": contact.contact_id,
                "name": contact.name, 
                "email": contact.email, 
                "phone": contact.phone, 
                "created_at": contact.created_at, 
                "updated_at": contact.updated_at
            })
        
        return {
            "message": "Contacts retrieved successfully!",
            "contacts": contacts,
            "count": str(len(contacts))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()

def getUserContactByID(username: str, contact_id: str) -> Dict[str, Any]:
    """
    Get a specific contact by ID for a user
    
    Args:
        username: Username of the contact owner
        contact_id: ID of the contact to retrieve
        
    Returns:
        Dictionary with contact information
    """
    try:
        get_db_connection()
        
        contacts = []
        contact = Contacts.objects(user=username, contact_id=contact_id).first()
        
        if contact:
            contacts.append({
                "id": contact.contact_id,
                "name": contact.name, 
                "email": contact.email, 
                "phone": contact.phone, 
                "created_at": contact.created_at, 
                "updated_at": contact.updated_at
            })
        
        return {
            "message": "Contacts retrieved successfully!",
            "contacts": contacts,
            "count": str(len(contacts))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()

def saveUserContacts(username: str, userdata: Dict[str, str]) -> Dict[str, Any]:
    """
    Create a new contact for a user
    
    Args:
        username: Username of the contact owner
        userdata: Dictionary containing contact information
        
    Returns:
        Dictionary with result message and contact data
    """
    try:
        get_db_connection()
        
        # Verify user exists
        user = Users.objects(name=username).first()
        if not user:
            return {"message": "User not found!"}
        
        # Check if contact with email or phone already exists
        existing_contact = Contacts.objects(
            user=username
        ).filter(
            email=userdata["email"]
        ) | Contacts.objects(
            user=username
        ).filter(
            phone=userdata["phone"]
        )
        
        if existing_contact:
            return {"message": "Email or phone number already exists!"}
        
        # Create new contact
        contact = Contacts(
            user=username, 
            name=userdata["name"], 
            email=userdata["email"], 
            phone=userdata["phone"]
        )
        contact.save()
        
        return {
            "message": "Contact saved successfully!",
            "contact": userdata,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()

def updateUserContacts(username: str, contact_id: str, userdata: Dict[str, str]) -> Dict[str, str]:
    """
    Update a specific contact for a user
    
    Args:
        username: Username of the contact owner
        contact_id: ID of the contact to update
        userdata: Dictionary containing updated contact information
        
    Returns:
        Dictionary with result message
    """
    try:
        get_db_connection()
        
        # Verify user exists
        user = Users.objects(name=username).first()
        if not user:
            return {"message": "User not found!"}
        
        # Find contact to update
        contact = Contacts.objects(contact_id=contact_id, user=username).first()
        if not contact:
            return {"message": "Contact not found!"}
        
        # Update contact fields
        contact.update(
            set__name=userdata["name"],
            set__email=userdata["email"],
            set__phone=userdata["phone"],
            set__updated_at=datetime.utcnow()
        )
        
        return {"message": "Contact updated successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()

def deleteUserContacts(username: str, contact_id: str) -> Dict[str, str]:
    """
    Delete a specific contact for a user
    
    Args:
        username: Username of the contact owner
        contact_id: ID of the contact to delete
        
    Returns:
        Dictionary with result message
    """
    try:
        get_db_connection()
        
        # Verify user exists
        user = Users.objects(name=username).first()
        if not user:
            return {"message": "User not found!"}
        
        # Find contact to delete
        contact = Contacts.objects(contact_id=contact_id, user=username).first()
        if not contact:
            return {"message": "Contact not found!"}
        
        # Delete the contact
        contact.delete()
        
        return {"message": "Contact deleted successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        disconnect()
