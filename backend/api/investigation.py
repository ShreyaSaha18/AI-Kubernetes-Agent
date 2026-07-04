"""Investigation API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from services.investigation_service import InvestigationService
from services.database_service import DatabaseService

router = APIRouter(prefix="/api", tags=["investigation"])

investigation_service = InvestigationService()

@router.post("/investigate")
async def investigate(user_id: str = Query(...)):
    """
    Run Kubernetes investigation with AI reasoning.

    Process:
    1. Collect Kubernetes evidence:
       - Pod status and health
       - Container logs
       - Kubernetes events
       - Deployment rollout status
       - Networking configuration
    2. AI Analysis:
       - Root cause analysis
       - Suggested fixes
       - Confidence scoring
    3. Save to database

    Returns structured investigation data + AI diagnosis.
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        result = await investigation_service.run_investigation()

        if result.get("diagnosis"):
            diagnosis = result["diagnosis"]

            db_result = await DatabaseService.save_investigation(
                user_id=user_id,
                root_cause=diagnosis.get("root_cause", ""),
                explanation=diagnosis.get("explanation", ""),
                fix=diagnosis.get("fix", ""),
                kubectl_command=diagnosis.get("kubectl_command", ""),
                confidence=diagnosis.get("confidence", 0),
                investigation_data=result.get("investigation")
            )

            result["investigation_id"] = db_result.get("investigation_id")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investigation endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investigations")
async def get_investigations(user_id: str = Query(...), limit: int = Query(10)):
    """Get investigation history for user"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        result = await DatabaseService.get_user_investigations(user_id, limit)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {
            "status": "success",
            "investigations": result["investigations"],
            "total": result["total"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get investigations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investigations/{investigation_id}")
async def get_investigation(investigation_id: str, user_id: str = Query(...)):
    """Get investigation details"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        result = await DatabaseService.get_investigation(investigation_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail="Investigation not found")

        investigation = result["investigation"]

        if investigation.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        return {
            "status": "success",
            "investigation": investigation
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get investigation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/investigations/{investigation_id}")
async def delete_investigation(investigation_id: str, user_id: str = Query(...)):
    """Delete investigation"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        result = await DatabaseService.delete_investigation(investigation_id, user_id)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete investigation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investigate/status")
async def investigation_status():
    """Check investigation endpoint health"""
    return {
        "status": "ready",
        "service": "kubernetes-investigation-layer",
        "ai_enabled": True,
        "database_enabled": True
    }
