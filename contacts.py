from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any

# Local imports
from jwtsign import verify_token
from database import (
    getUserContacts,
    saveUserContacts,
    updateUserContacts,
    deleteUserContacts,
    getUserContactByID
)
from models import Contact

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", status_code=status.HTTP_201_CREATED)
def save_contact(contact: Contact, payload: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Create a new contact for the authenticated user
    """
    user_id = payload['sub']
    contacts = saveUserContacts(user_id, contact.dict())
    return contacts

@router.get("/", status_code=status.HTTP_200_OK)
def get_contacts(payload: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get all contacts for the authenticated user
    """
    user_id = payload['sub']
    contacts = getUserContacts(user_id)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No contacts found"
        )
    return contacts

@router.get("/{contact_id}", status_code=status.HTTP_200_OK)
def get_contact_by_id(contact_id: str, payload: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get a specific contact by ID for the authenticated user
    """
    user_id = payload['sub']
    contact = getUserContactByID(user_id, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contact not found"
        )
    return contact

@router.put("/update/{contact_id}", status_code=status.HTTP_200_OK)
def update_contact(
    contact_id: str, 
    contact: Contact, 
    payload: dict = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Update a specific contact by ID for the authenticated user
    """
    user_id = payload['sub']
    result = updateUserContacts(user_id, contact_id, contact.dict())
    return result

@router.delete("/delete/{contact_id}", status_code=status.HTTP_200_OK)
def delete_contact(contact_id: str, payload: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Delete a specific contact by ID for the authenticated user
    """
    user_id = payload['sub']
    result = deleteUserContacts(user_id, contact_id)
    return result
