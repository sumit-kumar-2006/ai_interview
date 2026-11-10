import os
import pytest
from backend.app.services.llm_provider import (
    LLMProvider,
    GeminiProvider,
    OpenAIProvider,
    OllamaProvider,
    get_configured_llm_provider
)

def test_provider_fallback_when_unconfigured(monkeypatch):
    """When no LLM keys are present in env, get_configured_llm_provider returns None cleanly."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    
    provider = get_configured_llm_provider()
    assert provider is None

def test_gemini_provider_configured(monkeypatch):
    """When GEMINI_API_KEY is present, GeminiProvider is instantiated."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key_12345")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    
    provider = get_configured_llm_provider()
    assert isinstance(provider, GeminiProvider)
    assert provider.name == "gemini"

def test_openai_provider_configured(monkeypatch):
    """When OPENAI_API_KEY is present without Gemini, OpenAIProvider is instantiated."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    
    provider = get_configured_llm_provider()
    assert isinstance(provider, OpenAIProvider)
    assert provider.name == "openai"

def test_mock_structured_question_generation(monkeypatch):
    """Test LLM provider generating structured question and evaluation spec."""
    class MockProvider(LLMProvider):
        @property
        def name(self):
            return "mock"
            
        def generate_text(self, prompt: str) -> str:
            return """
            {
                "question": "How do you manage database connections efficiently in a high-traffic FastAPI application?",
                "category": "FastAPI & Async Architecture",
                "difficulty": "Hard",
                "expected_answer": "Use connection pooling with an async engine such as asyncpg with SQLAlchemy 2.0 or databases library to reuse connections and avoid per-request handshake overhead.",
                "required_concepts": ["connection pooling", "async engine / asyncpg", "reuse connections"],
                "optional_concepts": ["pool size", "max overflow", "disconnect handling"],
                "acceptable_alternatives": ["Using Tortoise-ORM or Tortoise connection pool"],
                "common_misconceptions": ["Creating a new engine per request", "Using sync blocking drivers inside async endpoints"],
                "rubric": {
                    "connection_pool_explanation": 50,
                    "async_driver_usage": 30,
                    "pool_sizing_tuning": 20
                },
                "follow_up_criteria": "Ask how connection timeouts and pool exhaustions are mitigated under load spikes."
            }
            """
    
    mock = MockProvider()
    q = mock.generate_interview_question(
        role="FastAPI Engineer",
        skills=["FastAPI", "SQLAlchemy", "PostgreSQL"],
        experience_level="Senior"
    )
    
    assert q is not None
    assert "question" in q
    assert "FastAPI" in q["question"]
    assert "evaluation_spec" in q
    assert "connection pooling" in q["evaluation_spec"]["required_concepts"]
    assert q["evaluation_spec"]["rubric"]["connection_pool_explanation"] == 50
