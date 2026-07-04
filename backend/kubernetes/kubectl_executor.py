"""Kubectl command executor - safe wrapper for kubectl commands"""

import subprocess
from typing import Dict, Any, List
from loguru import logger

class KubectlExecutor:
    """Execute kubectl commands safely and return structured output"""

    @staticmethod
    def execute(command: List[str]) -> Dict[str, Any]:
        """Execute kubectl command and return structured result"""
        try:
            logger.info(f"Executing: {' '.join(command)}")

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": None
                }
            else:
                error_msg = result.stderr or "Command failed"
                logger.warning(f"kubectl failed: {error_msg}")
                return {
                    "success": False,
                    "output": None,
                    "error": error_msg
                }
        except subprocess.TimeoutExpired:
            logger.error("kubectl command timed out")
            return {
                "success": False,
                "output": None,
                "error": "Command timed out after 30 seconds"
            }
        except FileNotFoundError:
            logger.error("kubectl not found")
            return {
                "success": False,
                "output": None,
                "error": "kubectl is not installed or not in PATH"
            }
        except Exception as e:
            logger.error(f"kubectl execution error: {str(e)}")
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }

    @staticmethod
    def get_pods() -> Dict[str, Any]:
        """Get all pods across all namespaces"""
        return KubectlExecutor.execute(["kubectl", "get", "pods", "-A", "-o", "json"])

    @staticmethod
    def get_events() -> Dict[str, Any]:
        """Get all events across all namespaces"""
        return KubectlExecutor.execute(["kubectl", "get", "events", "-A", "-o", "json"])

    @staticmethod
    def get_logs(pod_name: str, namespace: str = "default", tail: int = 100) -> Dict[str, Any]:
        """Get logs for a specific pod"""
        return KubectlExecutor.execute([
            "kubectl", "logs", pod_name,
            "-n", namespace,
            f"--tail={tail}",
            "--timestamps=true"
        ])

    @staticmethod
    def describe_deployment(deployment_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Describe a deployment"""
        return KubectlExecutor.execute([
            "kubectl", "describe", "deployment", deployment_name,
            "-n", namespace
        ])

    @staticmethod
    def get_services() -> Dict[str, Any]:
        """Get all services across all namespaces"""
        return KubectlExecutor.execute(["kubectl", "get", "services", "-A", "-o", "json"])

    @staticmethod
    def get_deployments() -> Dict[str, Any]:
        """Get all deployments across all namespaces"""
        return KubectlExecutor.execute(["kubectl", "get", "deployments", "-A", "-o", "json"])
