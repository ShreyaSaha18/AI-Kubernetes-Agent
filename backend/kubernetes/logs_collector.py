"""Logs collector - fetches logs from failed pods"""

from typing import Dict, Any, List
from loguru import logger
from .kubectl_executor import KubectlExecutor
from .pod_inspector import PodInspector

class LogsCollector:
    """Collect logs from problematic pods"""

    ERROR_KEYWORDS = [
        "error",
        "exception",
        "failed",
        "fatal",
        "panic",
        "crash",
        "connection refused",
        "timeout",
        "cannot find",
        "not found",
        "missing",
        "permission denied",
        "unauthorized",
        "invalid"
    ]

    @staticmethod
    def collect() -> Dict[str, Any]:
        """Collect logs from problematic pods"""
        logger.info("Starting logs collection")

        pod_inspection = PodInspector.inspect()

        if not pod_inspection["healthy"] is False:
            return {
                "total_logs_collected": 0,
                "logs": [],
                "error": "No problematic pods to collect logs from"
            }

        logs_data = []

        for pod in pod_inspection.get("problematic_pods", []):
            pod_name = pod.get("name")
            namespace = pod.get("namespace", "default")

            logger.info(f"Collecting logs from {namespace}/{pod_name}")

            log_result = KubectlExecutor.get_logs(pod_name, namespace)

            if log_result["success"]:
                logs = log_result["output"]
                relevant_lines = LogsCollector._filter_relevant_logs(logs)

                logs_data.append({
                    "pod": pod_name,
                    "namespace": namespace,
                    "status": pod.get("status"),
                    "logs": relevant_lines,
                    "error": None
                })
            else:
                logs_data.append({
                    "pod": pod_name,
                    "namespace": namespace,
                    "status": pod.get("status"),
                    "logs": [],
                    "error": log_result["error"]
                })

        logger.info(f"Logs collection complete: {len(logs_data)} pods")

        return {
            "total_logs_collected": len(logs_data),
            "logs": logs_data,
            "error": None
        }

    @staticmethod
    def _filter_relevant_logs(logs: str, max_lines: int = 50) -> List[str]:
        """Filter logs to show only relevant error lines"""
        lines = logs.split("\n")
        relevant = []

        for line in lines:
            if any(keyword in line.lower() for keyword in LogsCollector.ERROR_KEYWORDS):
                relevant.append(line.strip())

        if not relevant:
            relevant = [line.strip() for line in lines[-10:] if line.strip()]

        return relevant[:max_lines]
