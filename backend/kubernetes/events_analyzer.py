"""Events analyzer - analyzes Kubernetes events for issues"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from .kubectl_executor import KubectlExecutor

class EventsAnalyzer:
    """Analyze Kubernetes events to detect issues"""

    ISSUE_REASONS = {
        "FailedScheduling",
        "BackOff",
        "FailedMount",
        "FailedPull",
        "ErrImagePull",
        "Unhealthy",
        "FailedCreatePodSandbox",
        "FailedAttachVolume",
        "FailedDetachVolume",
        "FailedDelete",
        "NodeNotReady",
        "Evicted"
    }

    @staticmethod
    def analyze() -> Dict[str, Any]:
        """Analyze Kubernetes events"""
        logger.info("Starting events analysis")

        result = KubectlExecutor.get_events()

        if not result["success"]:
            return {
                "total_events": 0,
                "issues_found": [],
                "error": result["error"]
            }

        try:
            events_data = json.loads(result["output"])
            issues = []

            now = datetime.utcnow()
            recent_threshold = now - timedelta(hours=1)

            for event in events_data.get("items", []):
                reason = event.get("reason", "")
                message = event.get("message", "")
                event_type = event.get("type", "")

                if reason in EventsAnalyzer.ISSUE_REASONS or event_type == "Warning":
                    involved_object = event.get("involvedObject", {})

                    issues.append({
                        "reason": reason,
                        "message": message,
                        "type": event_type,
                        "object_kind": involved_object.get("kind"),
                        "object_name": involved_object.get("name"),
                        "namespace": involved_object.get("namespace", "default"),
                        "count": event.get("count", 1),
                        "first_timestamp": event.get("firstTimestamp"),
                        "last_timestamp": event.get("lastTimestamp")
                    })

            logger.info(f"Events analysis complete: {len(issues)} issues found")

            return {
                "total_events": len(events_data.get("items", [])),
                "issues_found": issues,
                "error": None
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse events: {str(e)}")
            return {
                "total_events": 0,
                "issues_found": [],
                "error": f"Failed to parse events: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Events analysis error: {str(e)}")
            return {
                "total_events": 0,
                "issues_found": [],
                "error": str(e)
            }
