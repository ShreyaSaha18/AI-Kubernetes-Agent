"""Kubernetes Agent - Senior SRE AI orchestrator"""

from typing import Dict, Any
from loguru import logger
from .root_cause_analyzer import RootCauseAnalyzer

class KubernetesAgent:
    """AI-powered Kubernetes troubleshooting agent"""

    def __init__(self):
        self.analyzer = RootCauseAnalyzer()

    async def diagnose(self, investigation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose Kubernetes issues using AI reasoning.

        Behaves like a Senior Kubernetes SRE helping troubleshoot incidents.
        """
        logger.info("Kubernetes Agent starting diagnosis")

        has_issues = self._check_for_issues(investigation)

        if not has_issues:
            return {
                "status": "success",
                "diagnosis": {
                    "root_cause": "No issues detected",
                    "explanation": "Cluster appears to be healthy",
                    "fix": "No action needed",
                    "kubectl_command": "N/A",
                    "prevention": "Continue monitoring",
                    "confidence": 100
                }
            }

        analysis_result = await self.analyzer.analyze(investigation)

        return analysis_result

    @staticmethod
    def _check_for_issues(investigation: Dict[str, Any]) -> bool:
        """Check if investigation found any issues"""
        pods = investigation.get("pods", {})
        if pods.get("problematic_pods"):
            return True

        logs = investigation.get("logs", {})
        if logs.get("logs"):
            return True

        events = investigation.get("events", {})
        if events.get("issues_found"):
            return True

        deployments = investigation.get("deployments", {})
        if deployments.get("unhealthy_deployments"):
            return True

        network = investigation.get("network", {})
        if network.get("services_with_issues"):
            return True

        return False
