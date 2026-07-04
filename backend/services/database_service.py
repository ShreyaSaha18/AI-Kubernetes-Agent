"""Database service - InsForge integration"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from models.database import Investigation, InvestigationHistory

class DatabaseService:
    """Manage investigations and users in InsForge database"""

    # In-memory storage for demo (replace with actual InsForge integration)
    _investigations: Dict[str, Investigation] = {}
    _users: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    async def save_investigation(
        user_id: str,
        root_cause: str,
        explanation: str,
        fix: str,
        kubectl_command: str,
        confidence: int,
        investigation_data: Optional[dict] = None
    ) -> Dict[str, Any]:
        """Save investigation to database"""
        try:
            investigation_id = f"inv_{datetime.utcnow().timestamp()}"
            timestamp = datetime.utcnow().isoformat()

            investigation = Investigation(
                id=investigation_id,
                user_id=user_id,
                root_cause=root_cause,
                explanation=explanation,
                fix=fix,
                kubectl_command=kubectl_command,
                confidence=confidence,
                timestamp=timestamp,
                investigation_data=investigation_data
            )

            DatabaseService._investigations[investigation_id] = investigation

            logger.info(f"Investigation saved: {investigation_id}")

            return {
                "success": True,
                "investigation_id": investigation_id,
                "timestamp": timestamp
            }

        except Exception as e:
            logger.error(f"Failed to save investigation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def get_user_investigations(
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get investigation history for user"""
        try:
            user_investigations = [
                inv for inv in DatabaseService._investigations.values()
                if inv.user_id == user_id
            ]

            # Sort by timestamp descending
            user_investigations.sort(
                key=lambda x: x.timestamp or "",
                reverse=True
            )

            history = [
                InvestigationHistory(
                    id=inv.id,
                    root_cause=inv.root_cause,
                    confidence=inv.confidence,
                    timestamp=inv.timestamp or "",
                    status=inv.status
                )
                for inv in user_investigations[:limit]
            ]

            logger.info(f"Retrieved {len(history)} investigations for user {user_id}")

            return {
                "success": True,
                "investigations": [h.dict() for h in history],
                "total": len(user_investigations)
            }

        except Exception as e:
            logger.error(f"Failed to get investigations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "investigations": []
            }

    @staticmethod
    async def get_investigation(investigation_id: str) -> Dict[str, Any]:
        """Get investigation details"""
        try:
            investigation = DatabaseService._investigations.get(investigation_id)

            if not investigation:
                return {
                    "success": False,
                    "error": "Investigation not found"
                }

            logger.info(f"Retrieved investigation {investigation_id}")

            return {
                "success": True,
                "investigation": investigation.dict()
            }

        except Exception as e:
            logger.error(f"Failed to get investigation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def delete_investigation(investigation_id: str, user_id: str) -> Dict[str, Any]:
        """Delete investigation (only owner can delete)"""
        try:
            investigation = DatabaseService._investigations.get(investigation_id)

            if not investigation:
                return {
                    "success": False,
                    "error": "Investigation not found"
                }

            if investigation.user_id != user_id:
                return {
                    "success": False,
                    "error": "Not authorized to delete this investigation"
                }

            del DatabaseService._investigations[investigation_id]

            logger.info(f"Deleted investigation {investigation_id}")

            return {
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to delete investigation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def create_user(email: str, user_id: str) -> Dict[str, Any]:
        """Create user record"""
        try:
            if email in DatabaseService._users:
                return {
                    "success": False,
                    "error": "User already exists"
                }

            user = {
                "id": user_id,
                "email": email,
                "created_at": datetime.utcnow().isoformat()
            }

            DatabaseService._users[email] = user

            logger.info(f"User created: {email}")

            return {
                "success": True,
                "user": user
            }

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def get_user(email: str) -> Dict[str, Any]:
        """Get user by email"""
        try:
            user = DatabaseService._users.get(email)

            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }

            return {
                "success": True,
                "user": user
            }

        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
