"""Cluster management API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from kubernetes.kubeconfig_parser import KubeconfigParser

router = APIRouter(prefix="/api/clusters", tags=["clusters"])

@router.get("/list")
async def list_clusters():
    """Get all available Kubernetes clusters from kubeconfig"""
    try:
        result = KubeconfigParser.get_clusters()

        if not result["success"]:
            logger.warning(f"Failed to get clusters: {result.get('error')}")
            return {
                "status": "error",
                "error": result.get("error"),
                "clusters": []
            }

        return {
            "status": "success",
            "error": None,
            "clusters": result["clusters"]
        }

    except Exception as e:
        logger.error(f"Cluster listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch")
async def switch_cluster(cluster_name: str = Query(...)):
    """Switch to a different Kubernetes cluster"""
    try:
        if not cluster_name:
            raise HTTPException(status_code=400, detail="Cluster name required")

        result = KubeconfigParser.set_current_context(cluster_name)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {
            "status": "success",
            "message": result.get("message")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cluster switch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
