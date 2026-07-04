"""Investigation service - orchestrates Kubernetes investigation and AI reasoning"""

from typing import Dict, Any
from loguru import logger
from datetime import datetime

from kubernetes.pod_inspector import PodInspector
from kubernetes.logs_collector import LogsCollector
from kubernetes.events_analyzer import EventsAnalyzer
from kubernetes.deployment_inspector import DeploymentInspector
from kubernetes.network_inspector import NetworkInspector
from ai.kubernetes_agent import KubernetesAgent

class InvestigationService:
    """Orchestrate Kubernetes investigation and AI reasoning"""

    def __init__(self):
        self.agent = KubernetesAgent()

    async def run_investigation(self) -> Dict[str, Any]:
        """Run complete Kubernetes investigation with AI reasoning"""
        logger.info("Starting Kubernetes investigation and analysis")

        start_time = datetime.utcnow().isoformat()

        try:
            pods = PodInspector.inspect()
            logger.info("Pod inspection done")

            logs = LogsCollector.collect()
            logger.info("Logs collection done")

            events = EventsAnalyzer.analyze()
            logger.info("Events analysis done")

            deployments = DeploymentInspector.inspect()
            logger.info("Deployment inspection done")

            network = NetworkInspector.inspect()
            logger.info("Network inspection done")

            investigation_data = {
                "pods": pods,
                "logs": logs,
                "events": events,
                "deployments": deployments,
                "network": network
            }

            diagnosis_result = await self.agent.diagnose(investigation_data)
            logger.info("AI diagnosis complete")

            response = {
                "status": "success",
                "timestamp": start_time,
                "investigation": investigation_data,
                "diagnosis": diagnosis_result.get("diagnosis"),
                "diagnosis_status": diagnosis_result.get("status"),
                "diagnosis_error": diagnosis_result.get("error")
            }

            logger.info("Kubernetes investigation and analysis complete")
            return response

        except Exception as e:
            logger.error(f"Investigation failed: {str(e)}")
            return {
                "status": "error",
                "timestamp": start_time,
                "error": str(e),
                "investigation": None,
                "diagnosis": None
            }
