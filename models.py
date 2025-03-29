import uuid
from datetime import datetime

from mongoengine import Document, StringField, EmailField, DateTimeField
from pydantic import BaseModel, Field, EmailStr

# Generate a unique ID
def generate_id() -> str:
    """Generate a unique hex ID using UUID4"""
    return uuid.uuid4().hex

# MongoDB Document Models
class Users(Document):
    """MongoDB model for storing user information"""
    user_id = StringField(default=generate_id, primary_key=True)
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['email'], 'unique': True}
        ]
    }

class Contacts(Document):
    """MongoDB model for storing contact information"""
    contact_id = StringField(default=generate_id, primary_key=True)
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    phone = StringField(required=True, unique=True)
    user = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'contacts',
        'indexes': [
            {'fields': ['email'], 'unique': True},
            {'fields': ['phone'], 'unique': True},
            {'fields': ['user', 'contact_id']}
        ]
    }

# Pydantic Models for API Request/Response
class UserRegister(BaseModel):
    """Schema for user registration"""
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="securepassword123", min_length=8)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="securepassword123")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }

class Contact(BaseModel):
    """Schema for contact creation and update"""
    name: str = Field(..., example="Jane Smith")
    email: EmailStr = Field(..., example="jane@example.com")
    phone: str = Field(..., example="+1234567890")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1234567890"
            }
        }

class ContactResponse(BaseModel):
    """Schema for contact response"""
    id: str
    name: str
    email: str
    phone: str
    created_at: datetime
    updated_at: datetime
