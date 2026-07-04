"""Prompt Builder - Structured Kubernetes troubleshooting prompts"""

from typing import Dict, Any
import json

class PromptBuilder:
    """Build structured prompts for Kubernetes troubleshooting"""

    SYSTEM_PROMPT = """You are a Senior Kubernetes SRE expert with 10+ years of experience.

Your role is to analyze Kubernetes cluster issues and provide expert-level troubleshooting guidance.

When analyzing issues:
1. Correlate pod status, logs, events, and deployment state
2. Identify root causes, not just symptoms
3. Provide practical, actionable fixes
4. Include specific kubectl commands
5. Suggest prevention measures
6. Rate your confidence level

Respond ONLY with valid JSON in this exact format:
{
  "root_cause": "...",
  "explanation": "...",
  "fix": "...",
  "kubectl_command": "...",
  "prevention": "...",
  "confidence": 0-100
}

Be concise but thorough. Avoid speculation."""

    @staticmethod
    def build_investigation_prompt(investigation: Dict[str, Any]) -> list:
        """Build messages for LLM from investigation data"""

        investigation_summary = PromptBuilder._format_investigation(investigation)

        messages = [
            {
                "role": "system",
                "content": PromptBuilder.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""Analyze this Kubernetes cluster issue and provide diagnosis:

{investigation_summary}

Provide your analysis in JSON format with: root_cause, explanation, fix, kubectl_command, prevention, and confidence."""
            }
        ]

        return messages

    @staticmethod
    def _format_investigation(investigation: Dict[str, Any]) -> str:
        """Format investigation data into readable summary"""

        summary_parts = []

        # Pods
        pods = investigation.get("pods", {})
        if pods.get("error"):
            summary_parts.append(f"[PODS] Error: {pods['error']}")
        else:
            if pods.get("problematic_pods"):
                summary_parts.append("[PODS] Issues found:")
                for pod in pods["problematic_pods"][:5]:
                    summary_parts.append(
                        f"  - {pod.get('name')} ({pod.get('namespace')}): {pod.get('status')}"
                    )
            else:
                summary_parts.append(f"[PODS] Healthy ({pods.get('total_pods', 0)} total)")

        # Logs
        logs = investigation.get("logs", {})
        if logs.get("logs"):
            summary_parts.append("[LOGS] Error messages:")
            for log_entry in logs["logs"][:3]:
                pod_name = log_entry.get("pod")
                log_lines = log_entry.get("logs", [])[:5]
                if log_lines:
                    summary_parts.append(f"  From {pod_name}:")
                    for line in log_lines:
                        summary_parts.append(f"    {line}")

        # Events
        events = investigation.get("events", {})
        if events.get("issues_found"):
            summary_parts.append("[EVENTS] Warnings/Errors:")
            for event in events["issues_found"][:5]:
                summary_parts.append(
                    f"  - {event.get('reason')}: {event.get('message')}"
                )

        # Deployments
        deployments = investigation.get("deployments", {})
        if deployments.get("unhealthy_deployments"):
            summary_parts.append("[DEPLOYMENTS] Rollout issues:")
            for dep in deployments["unhealthy_deployments"][:3]:
                summary_parts.append(
                    f"  - {dep.get('name')}: {dep.get('ready_replicas')}/{dep.get('desired_replicas')} ready"
                )

        # Network
        network = investigation.get("network", {})
        if network.get("services_with_issues"):
            summary_parts.append("[NETWORK] Service issues:")
            for svc in network["services_with_issues"][:3]:
                summary_parts.append(
                    f"  - {svc.get('name')}: {svc.get('issue')}"
                )

        return "\n".join(summary_parts)
