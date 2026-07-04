"""Pod inspector - checks pod status and detects unhealthy pods"""

import json
from typing import Dict, Any, List
from loguru import logger
from .kubectl_executor import KubectlExecutor

class PodInspector:
    """Inspect pods and detect unhealthy states"""

    UNHEALTHY_STATUSES = {
        "CrashLoopBackOff",
        "ImagePullBackOff",
        "Pending",
        "Error",
        "OOMKilled",
        "ContainerCreating",
        "Unknown",
        "Terminating"
    }

    @staticmethod
    def inspect() -> Dict[str, Any]:
        """Inspect all pods and detect issues"""
        logger.info("Starting pod inspection")

        result = KubectlExecutor.get_pods()

        if not result["success"]:
            return {
                "healthy": None,
                "error": result["error"],
                "problematic_pods": []
            }

        try:
            pods_data = json.loads(result["output"])
            problematic_pods = []

            for pod in pods_data.get("items", []):
                status = pod.get("status", {}).get("phase", "Unknown")
                name = pod.get("metadata", {}).get("name")
                namespace = pod.get("metadata", {}).get("namespace", "default")

                # Check pod phase
                if status in PodInspector.UNHEALTHY_STATUSES:
                    problematic_pods.append({
                        "name": name,
                        "namespace": namespace,
                        "status": status,
                        "phase": status
                    })
                    continue

                # Check container statuses for more detailed issues
                container_statuses = pod.get("status", {}).get("containerStatuses", [])
                for container in container_statuses:
                    if not container.get("ready", False):
                        state = container.get("state", {})
                        if "waiting" in state:
                            reason = state["waiting"].get("reason", "Unknown")
                            problematic_pods.append({
                                "name": name,
                                "namespace": namespace,
                                "status": reason,
                                "container": container.get("name"),
                                "phase": status
                            })

            is_healthy = len(problematic_pods) == 0
            logger.info(f"Pod inspection complete: {len(problematic_pods)} issues found")

            return {
                "healthy": is_healthy,
                "total_pods": len(pods_data.get("items", [])),
                "problematic_pods": problematic_pods,
                "error": None
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pod data: {str(e)}")
            return {
                "healthy": None,
                "error": f"Failed to parse kubectl output: {str(e)}",
                "problematic_pods": []
            }
        except Exception as e:
            logger.error(f"Pod inspection error: {str(e)}")
            return {
                "healthy": None,
                "error": str(e),
                "problematic_pods": []
            }
