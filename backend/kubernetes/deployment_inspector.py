"""Deployment inspector - inspects deployments for issues"""

import json
from typing import Dict, Any
from loguru import logger
from .kubectl_executor import KubectlExecutor

class DeploymentInspector:
    """Inspect deployments and detect rollout issues"""

    @staticmethod
    def inspect() -> Dict[str, Any]:
        """Inspect all deployments"""
        logger.info("Starting deployment inspection")

        result = KubectlExecutor.get_deployments()

        if not result["success"]:
            return {
                "total_deployments": 0,
                "unhealthy_deployments": [],
                "error": result["error"]
            }

        try:
            deployments_data = json.loads(result["output"])
            unhealthy = []

            for deployment in deployments_data.get("items", []):
                metadata = deployment.get("metadata", {})
                spec = deployment.get("spec", {})
                status = deployment.get("status", {})

                name = metadata.get("name")
                namespace = metadata.get("namespace", "default")

                desired_replicas = spec.get("replicas", 0)
                ready_replicas = status.get("readyReplicas", 0)
                available_replicas = status.get("availableReplicas", 0)
                updated_replicas = status.get("updatedReplicas", 0)

                is_healthy = (
                    ready_replicas == desired_replicas and
                    available_replicas == desired_replicas
                )

                if not is_healthy:
                    conditions = status.get("conditions", [])
                    condition_status = []
                    for condition in conditions:
                        condition_status.append({
                            "type": condition.get("type"),
                            "status": condition.get("status"),
                            "reason": condition.get("reason"),
                            "message": condition.get("message")
                        })

                    unhealthy.append({
                        "name": name,
                        "namespace": namespace,
                        "desired_replicas": desired_replicas,
                        "ready_replicas": ready_replicas,
                        "available_replicas": available_replicas,
                        "updated_replicas": updated_replicas,
                        "conditions": condition_status
                    })

            logger.info(f"Deployment inspection complete: {len(unhealthy)} unhealthy deployments")

            return {
                "total_deployments": len(deployments_data.get("items", [])),
                "unhealthy_deployments": unhealthy,
                "error": None
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse deployments: {str(e)}")
            return {
                "total_deployments": 0,
                "unhealthy_deployments": [],
                "error": f"Failed to parse deployments: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Deployment inspection error: {str(e)}")
            return {
                "total_deployments": 0,
                "unhealthy_deployments": [],
                "error": str(e)
            }
