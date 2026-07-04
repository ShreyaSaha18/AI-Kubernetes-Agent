"""LLM Client - OpenRouter integration"""

import httpx
from typing import Dict, Any, Optional
from loguru import logger
from core.config import settings

class LLMClient:
    """OpenRouter LLM client for AI reasoning"""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 60

    async def generate(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response from LLM"""
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY not configured")
            return {
                "success": False,
                "error": "OpenRouter API key not configured",
                "response": None
            }

        try:
            logger.info(f"Sending request to OpenRouter ({self.model})")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://ai-kubernetes-agent.local",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": 2000
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info("LLM response received successfully")
                    return {
                        "success": True,
                        "error": None,
                        "response": content
                    }
                else:
                    error_msg = f"OpenRouter API error: {response.status_code}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "response": None
                    }

        except httpx.TimeoutException:
            error_msg = "OpenRouter request timed out (60s)"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": None
            }
        except httpx.RequestError as e:
            error_msg = f"OpenRouter connection error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": None
            }
        except Exception as e:
            error_msg = f"LLM generation error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": None
            }
