from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

# Local imports
from models import UserRegister, UserLogin
from jwtsign import sign_user, decode_token
from database import saveUserToDB, getUserFromDB
import contacts

app = FastAPI(
    title="FastAPI JWT Authentication",
    description="API with JWT authentication and contact management",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup", tags=["Authentication"])
def sign_up(userdata: UserRegister) -> Dict[str, Any]:
    """
    Register a new user with name, email, and password
    """
    current_user = userdata.dict()
    result = saveUserToDB(current_user)
    return result

@app.post("/signin", tags=["Authentication"])
def sign_in(userdata: UserLogin) -> Dict[str, Any]:
    """
    Login with email and password to get a JWT token
    """
    current_user = userdata.dict()
    result = getUserFromDB(current_user)
    return result

# Include the contacts router
app.include_router(contacts.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
