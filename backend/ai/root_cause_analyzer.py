"""Root Cause Analyzer - Analyzes investigation data and correlates findings"""

import json
from typing import Dict, Any, Optional
from loguru import logger
from .llm_client import LLMClient
from .prompt_builder import PromptBuilder

class RootCauseAnalyzer:
    """Analyze Kubernetes issues and find root causes"""

    def __init__(self):
        self.llm_client = LLMClient()

    async def analyze(self, investigation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze investigation data and generate diagnosis"""
        logger.info("Starting root cause analysis")

        try:
            messages = PromptBuilder.build_investigation_prompt(investigation)

            llm_result = await self.llm_client.generate(messages)

            if not llm_result["success"]:
                return {
                    "status": "error",
                    "error": llm_result["error"],
                    "diagnosis": None
                }

            diagnosis = self._parse_diagnosis(llm_result["response"])

            if diagnosis:
                logger.info(f"Analysis complete: {diagnosis.get('root_cause')}")
                return {
                    "status": "success",
                    "error": None,
                    "diagnosis": diagnosis
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to parse LLM response",
                    "diagnosis": None
                }

        except Exception as e:
            logger.error(f"Root cause analysis error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "diagnosis": None
            }

    @staticmethod
    def _parse_diagnosis(response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response into structured diagnosis"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                diagnosis = json.loads(json_str)

                diagnosis = RootCauseAnalyzer._validate_diagnosis(diagnosis)
                return diagnosis
            else:
                logger.warning("No JSON found in LLM response")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Response parsing error: {str(e)}")
            return None

    @staticmethod
    def _validate_diagnosis(diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize diagnosis"""
        required_fields = {
            "root_cause": "Unknown cause",
            "explanation": "Unable to generate explanation",
            "fix": "Manual investigation required",
            "kubectl_command": "N/A",
            "prevention": "Implement monitoring",
            "confidence": 0
        }

        validated = {}
        for field, default in required_fields.items():
            value = diagnosis.get(field, default)

            if field == "confidence":
                try:
                    validated[field] = max(0, min(100, int(value)))
                except (ValueError, TypeError):
                    validated[field] = 0
            else:
                validated[field] = str(value).strip()

        return validated
