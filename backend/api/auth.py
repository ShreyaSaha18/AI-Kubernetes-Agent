"""Authentication API endpoints"""

from fastapi import APIRouter, HTTPException
from loguru import logger
import uuid

from models.database import AuthRequest, User
from services.database_service import DatabaseService

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
async def signup(request: AuthRequest):
    """Register new user"""
    try:
        email = request.email.lower().strip()

        if not email or not request.password:
            raise HTTPException(status_code=400, detail="Email and password required")

        existing = await DatabaseService.get_user(email)
        if existing["success"]:
            raise HTTPException(status_code=400, detail="User already exists")

        user_id = str(uuid.uuid4())

        result = await DatabaseService.create_user(email, user_id)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Signup failed"))

        session_id = str(uuid.uuid4())

        return {
            "status": "success",
            "user": {
                "id": user_id,
                "email": email
            },
            "access_token": session_id,
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Signup failed")

@router.post("/login")
async def login(request: AuthRequest):
    """Login user"""
    try:
        email = request.email.lower().strip()

        if not email or not request.password:
            raise HTTPException(status_code=400, detail="Email and password required")

        result = await DatabaseService.get_user(email)

        if not result["success"]:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = result["user"]
        session_id = str(uuid.uuid4())

        return {
            "status": "success",
            "user": {
                "id": user["id"],
                "email": user["email"]
            },
            "access_token": session_id,
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/logout")
async def logout():
    """Logout user"""
    return {
        "status": "success",
        "message": "Logged out"
    }

@router.get("/me")
async def get_current_user(user_id: str):
    """Get current user info"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        return {
            "status": "success",
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user")
