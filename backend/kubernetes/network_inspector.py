"""Network inspector - inspects services and networking"""

import json
from typing import Dict, Any
from loguru import logger
from .kubectl_executor import KubectlExecutor

class NetworkInspector:
    """Inspect services and networking configuration"""

    @staticmethod
    def inspect() -> Dict[str, Any]:
        """Inspect all services and networking"""
        logger.info("Starting network inspection")

        services_result = KubectlExecutor.get_services()

        if not services_result["success"]:
            return {
                "total_services": 0,
                "services_with_issues": [],
                "error": services_result["error"]
            }

        try:
            services_data = json.loads(services_result["output"])
            services_with_issues = []

            for service in services_data.get("items", []):
                metadata = service.get("metadata", {})
                spec = service.get("spec", {})
                status = service.get("status", {})

                name = metadata.get("name")
                namespace = metadata.get("namespace", "default")
                service_type = spec.get("type", "ClusterIP")
                selector = spec.get("selector", {})

                has_endpoints = len(status.get("loadBalancer", {}).get("ingress", [])) > 0 or service_type == "ClusterIP"

                issue = None
                if not selector:
                    issue = "No selector defined"
                elif service_type == "LoadBalancer" and not has_endpoints:
                    issue = "LoadBalancer has no endpoints assigned"

                if issue:
                    services_with_issues.append({
                        "name": name,
                        "namespace": namespace,
                        "type": service_type,
                        "selector": selector,
                        "issue": issue
                    })

            logger.info(f"Network inspection complete: {len(services_with_issues)} services with issues")

            return {
                "total_services": len(services_data.get("items", [])),
                "services_with_issues": services_with_issues,
                "error": None
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse services: {str(e)}")
            return {
                "total_services": 0,
                "services_with_issues": [],
                "error": f"Failed to parse services: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Network inspection error: {str(e)}")
            return {
                "total_services": 0,
                "services_with_issues": [],
                "error": str(e)
            }
