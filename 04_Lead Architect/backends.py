"""LLM backends: an offline scripted Mock plus Gemini, OpenAI (ChatGPT) and Claude adapters.

Only the standard library is used, so the repo runs in a fresh VS Code / Antigravity
workspace with no `pip install`. Live adapters read API keys from the environment.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Callable, Dict, Optional


class BackendError(RuntimeError):
    pass


class Backend:
    name = "base"
    model = ""
    live = False

    def complete(self, role: str, system: str, user: str) -> str:
        raise NotImplementedError

    @property
    def label(self) -> str:
        return f"{self.name}:{self.model}" if self.model else self.name


def _post(url: str, headers: Dict[str, str], body: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise BackendError(f"HTTP {exc.code} from {url}: {exc.read()[:300]!r}") from exc
    except urllib.error.URLError as exc:
        raise BackendError(f"Network error calling {url}: {exc.reason}") from exc


def _need_key(var: str) -> str:
    key = os.environ.get(var, "").strip()
    if not key:
        raise BackendError(f"Environment variable {var} is not set.")
    return key


class GeminiBackend(Backend):
    name = "gemini"
    live = True

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self._key = _need_key("GEMINI_API_KEY")

    def complete(self, role: str, system: str, user: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        data = _post(
            url,
            {"x-goog-api-key": self._key},
            {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
            },
        )
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as exc:
            raise BackendError(f"Unexpected Gemini response: {str(data)[:300]}") from exc


class OpenAIBackend(Backend):
    name = "openai"
    live = True

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")
        self._key = _need_key("OPENAI_API_KEY")

    def complete(self, role: str, system: str, user: str) -> str:
        data = _post(
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {self._key}"},
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise BackendError(f"Unexpected OpenAI response: {str(data)[:300]}") from exc


class ClaudeBackend(Backend):
    name = "claude"
    live = True

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
        self._key = _need_key("ANTHROPIC_API_KEY")

    def complete(self, role: str, system: str, user: str) -> str:
        data = _post(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": self._key, "anthropic-version": "2023-06-01"},
            {
                "model": self.model,
                "max_tokens": 700,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        try:
            return "".join(b.get("text", "") for b in data["content"]).strip()
        except (KeyError, TypeError) as exc:
            raise BackendError(f"Unexpected Claude response: {str(data)[:300]}") from exc


class MockBackend(Backend):
    """Offline backend. Each role maps to a handler: callable(user_prompt) -> str."""

    name = "mock"
    model = "scripted"
    live = False

    def __init__(self, handlers: Dict[str, Callable[[str], str]]):
        self.handlers = handlers

    def complete(self, role: str, system: str, user: str) -> str:
        if role not in self.handlers:
            raise BackendError(f"MockBackend has no handler for role '{role}'.")
        return self.handlers[role](user)


PROVIDERS = {"gemini": GeminiBackend, "openai": OpenAIBackend, "claude": ClaudeBackend}


def make_live_backend(provider: str) -> Backend:
    if provider not in PROVIDERS:
        raise BackendError(f"Unknown provider '{provider}'. Choose from {sorted(PROVIDERS)}.")
    return PROVIDERS[provider]()


def queue_handler(lines):
    """Return a handler that replays scripted lines, then 'I do not know.'"""
    it = iter(lines)

    def handler(_prompt: str) -> str:
        try:
            return next(it)
        except StopIteration:
            return "I do not know."

    return handler
