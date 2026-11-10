import os
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Base Provider abstraction for optional LLM integration (Google Gemini, OpenAI, Ollama, Anthropic).
    Configurable entirely through environment variables.
    If no provider is configured, methods return None so callers cleanly fall back
    to curated verified domain rubrics.
    """
    def __init__(self, name: str = "none"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider_name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return False

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        return None

    def generate_interview_question(
        self, role: str, skills: List[str], experience_level: str
    ) -> Optional[Dict[str, Any]]:
        prompt = f"Role: {role}, Skills: {', '.join(skills)}, Level: {experience_level}"
        data = None
        if hasattr(self, "generate_text"):
            try:
                txt = self.generate_text(prompt)  # type: ignore
                if txt:
                    clean_txt = txt.strip()
                    if clean_txt.startswith("```json"):
                        clean_txt = clean_txt[7:]
                    if clean_txt.startswith("```"):
                        clean_txt = clean_txt[3:]
                    if clean_txt.endswith("```"):
                        clean_txt = clean_txt[:-3]
                    data = json.loads(clean_txt.strip())
            except Exception as e:
                logger.warning(f"Failed to parse text as json: {e}")
        
        if not data:
            data = self.generate_json(prompt, "You are an expert technical interviewer.")

        if not data or not isinstance(data, dict):
            return None

        # Build standardized question and evaluation_spec
        eval_spec = data.get("evaluation_spec", {})
        if not eval_spec:
            eval_spec = {
                "required_concepts": data.get("required_concepts", []),
                "optional_concepts": data.get("optional_concepts", []),
                "acceptable_alternatives": data.get("acceptable_alternatives", []),
                "common_misconceptions": data.get("common_misconceptions", []),
                "rubric": data.get("rubric", {
                    "concept_accuracy": 40,
                    "technical_depth": 30,
                    "practical_application": 30
                }),
                "follow_up_criteria": data.get("follow_up_criteria", "")
            }

        return {
            "question": data.get("question", ""),
            "category": data.get("category", role),
            "difficulty": data.get("difficulty", "Medium"),
            "expected_answer": data.get("expected_answer", ""),
            "evaluation_spec": eval_spec
        }


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        super().__init__(name="gemini")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("LLM_MODEL", "").strip() or "gemini-1.5-flash"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return json.loads(text)
        except Exception as e:
            logger.warning(f"Gemini generation call failed: {e}")
        return None


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        super().__init__(name="openai")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("LLM_MODEL", "").strip() or "gpt-4o-mini"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        url = "https://api.openai.com/v1/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    return json.loads(text)
        except Exception as e:
            logger.warning(f"OpenAI generation call failed: {e}")
        return None


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None):
        super().__init__(name="ollama")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "").strip()).rstrip("/")
        self.model_name = model_name or os.getenv("LLM_MODEL", "").strip() or "llama3.2"

    def is_available(self) -> bool:
        return bool(self.base_url)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "format": "json",
            "stream": False
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                response_text = data.get("response", "")
                return json.loads(response_text)
        except Exception as e:
            logger.warning(f"Ollama generation call failed: {e}")
        return None


def get_configured_llm_provider() -> Optional[LLMProvider]:
    """
    Instantiates and returns the configured provider based on environment variables,
    or None if no supported provider is configured.
    """
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    ollama_url = os.getenv("OLLAMA_BASE_URL", "").strip()

    if explicit == "gemini" and gemini_key:
        return GeminiProvider(api_key=gemini_key)
    if explicit == "openai" and openai_key:
        return OpenAIProvider(api_key=openai_key)
    if explicit == "ollama" and ollama_url:
        return OllamaProvider(base_url=ollama_url)

    # Auto-detection
    if gemini_key:
        return GeminiProvider(api_key=gemini_key)
    if openai_key:
        return OpenAIProvider(api_key=openai_key)
    if ollama_url:
        return OllamaProvider(base_url=ollama_url)

    return None


class DynamicLLMProxy:
    """
    Transparent proxy that dynamically dispatches to whichever provider is currently
    configured in the environment. Defaults safely to no-op when unconfigured.
    """
    def is_available(self) -> bool:
        provider = get_configured_llm_provider()
        return provider is not None and provider.is_available()

    @property
    def provider_name(self) -> str:
        provider = get_configured_llm_provider()
        return provider.name if provider else "none"

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        provider = get_configured_llm_provider()
        if provider:
            return provider.generate_json(prompt, system_prompt)
        return None

    def generate_interview_question(
        self, role: str, skills: List[str], experience_level: str
    ) -> Optional[Dict[str, Any]]:
        provider = get_configured_llm_provider()
        if provider:
            return provider.generate_interview_question(role, skills, experience_level)
        return None


# Global active instance
llm_provider = DynamicLLMProxy()
