"""Kubeconfig parser - Extract clusters from kubeconfig"""

import os
import yaml
from typing import Dict, Any, List, Optional
from loguru import logger
from pathlib import Path

class KubeconfigParser:
    """Parse kubeconfig and extract cluster information"""

    @staticmethod
    def get_kubeconfig_path() -> Optional[str]:
        """Get kubeconfig path from environment or default"""
        kubeconfig = os.environ.get("KUBECONFIG")

        if kubeconfig:
            return kubeconfig

        home = Path.home()
        default_path = home / ".kube" / "config"

        if default_path.exists():
            return str(default_path)

        return None

    @staticmethod
    def get_clusters() -> Dict[str, Any]:
        """Get all clusters from kubeconfig"""
        try:
            kubeconfig_path = KubeconfigParser.get_kubeconfig_path()

            if not kubeconfig_path:
                logger.warning("No kubeconfig found")
                return {
                    "success": False,
                    "error": "No kubeconfig found. Check KUBECONFIG env var or ~/.kube/config",
                    "clusters": []
                }

            if not os.path.exists(kubeconfig_path):
                logger.warning(f"Kubeconfig not found at {kubeconfig_path}")
                return {
                    "success": False,
                    "error": f"Kubeconfig not found at {kubeconfig_path}",
                    "clusters": []
                }

            with open(kubeconfig_path, "r") as f:
                config = yaml.safe_load(f)

            if not config or "clusters" not in config:
                return {
                    "success": False,
                    "error": "No clusters found in kubeconfig",
                    "clusters": []
                }

            clusters = []
            for cluster_info in config.get("clusters", []):
                name = cluster_info.get("name", "unknown")
                cluster = cluster_info.get("cluster", {})
                server = cluster.get("server", "unknown")

                clusters.append({
                    "name": name,
                    "server": server,
                    "certificate_authority": cluster.get("certificate-authority", "N/A")
                })

            logger.info(f"Found {len(clusters)} cluster(s)")

            return {
                "success": True,
                "error": None,
                "clusters": clusters
            }

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse kubeconfig: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to parse kubeconfig: {str(e)}",
                "clusters": []
            }
        except Exception as e:
            logger.error(f"Kubeconfig parse error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "clusters": []
            }

    @staticmethod
    def set_current_context(cluster_name: str) -> Dict[str, Any]:
        """Set the current context to a specific cluster"""
        try:
            import subprocess

            result = subprocess.run(
                ["kubectl", "config", "use-context", cluster_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"Switched to context: {cluster_name}")
                return {
                    "success": True,
                    "error": None,
                    "message": f"Switched to context: {cluster_name}"
                }
            else:
                error_msg = result.stderr or "Failed to switch context"
                logger.error(f"Failed to switch context: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": None
                }

        except Exception as e:
            logger.error(f"Context switch error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": None
            }
