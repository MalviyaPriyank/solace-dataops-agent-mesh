#!/usr/bin/env python3
"""Expose a local Gyrus ADK agent as an A2A-compatible HTTP service."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a


def _add_gyrus_to_path(repo: Path) -> None:
    for path in (repo, repo / "src"):
        path_text = str(path)
        if path.exists() and path_text not in sys.path:
            sys.path.insert(0, path_text)


def _load_dotenv(repo: Path) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    env_file = repo / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def _load_agent(module_name: str, attr_name: str):
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr_name)
    except AttributeError as exc:
        raise SystemExit(
            f"Module {module_name!r} does not define {attr_name!r}."
        ) from exc


def main() -> None:
    gyrus_repo = Path(
        os.environ.get("GYRUS_REPO", "/Users/priyankmalviya/Desktop/opensource/Gyrus")
    ).expanduser()
    if not gyrus_repo.exists():
        raise SystemExit(
            "Set GYRUS_REPO to your local Gyrus checkout. "
            f"Current value does not exist: {gyrus_repo}"
        )

    _add_gyrus_to_path(gyrus_repo)
    _load_dotenv(gyrus_repo)

    module_name = os.environ.get(
        "GYRUS_A2A_AGENT_MODULE",
        "gyrus_ai.objagents.sub_agents.analytical.frosty.objagents.agent",
    )
    attr_name = os.environ.get("GYRUS_A2A_AGENT_ATTR", "root_agent")
    host = os.environ.get("GYRUS_A2A_HOST", "127.0.0.1")
    port = int(os.environ.get("GYRUS_A2A_PORT", "8004"))

    agent = _load_agent(module_name, attr_name)
    app = to_a2a(agent=agent, host=host, port=port, protocol="http")

    print(f"Loaded Gyrus agent: {getattr(agent, 'name', module_name)}")
    print(f"A2A endpoint: http://{host}:{port}")
    print(f"Agent card:   http://{host}:{port}/.well-known/agent-card.json")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
