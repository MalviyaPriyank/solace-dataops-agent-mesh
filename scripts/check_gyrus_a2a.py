#!/usr/bin/env python3
"""Smoke-test a local A2A endpoint without requiring Solace Agent Mesh."""

from __future__ import annotations

import json
import sys
import urllib.request
from typing import Any
from uuid import uuid4


def _read_json(url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if body is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _collect_text(value: Any) -> list[str]:
    if isinstance(value, dict):
        text = value.get("text")
        found = [text] if isinstance(text, str) else []
        for child in value.values():
            found.extend(_collect_text(child))
        return found
    if isinstance(value, list):
        found: list[str] = []
        for child in value:
            found.extend(_collect_text(child))
        return found
    return []


def _best_response_text(texts: list[str], prompt: str) -> str:
    seen: set[str] = set()
    candidates: list[str] = []
    for text in texts:
        normalized = text.strip()
        if not normalized or normalized == prompt or normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(normalized)

    for text in reversed(candidates):
        lowered = text.lower()
        if "the user is asking" not in lowered and "let me " not in lowered:
            return text
    return candidates[-1] if candidates else ""


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8004"
    prompt = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "Summarize how you would investigate a checkout data freshness incident in three bullets."
    )

    card = _read_json(f"{base_url.rstrip('/')}/.well-known/agent-card.json")
    print(f"Agent card: {card.get('name')} at {card.get('url')}")
    print(f"Skills: {', '.join(skill.get('name', skill.get('id', 'unknown')) for skill in card.get('skills', [])[:5])}")

    message_id = f"msg-{uuid4()}"
    payload = {
        "jsonrpc": "2.0",
        "id": f"demo-{uuid4()}",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": prompt}],
                "messageId": message_id,
                "contextId": "gyrus-solace-local-demo",
            }
        },
    }
    response = _read_json(base_url.rstrip("/"), payload)
    print("\nA2A response text:")
    texts = _collect_text(response.get("result", response))
    best_text = _best_response_text(texts, prompt)
    print(best_text if best_text else json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
