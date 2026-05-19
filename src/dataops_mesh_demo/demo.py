from __future__ import annotations

import argparse
import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable


Message = dict[str, Any]
Handler = Callable[[str, Message], Awaitable[None]]


TOPICS = {
    "incident_created": "dataops/incidents/created",
    "incident_classified": "dataops/incidents/classified",
    "postgres_request": "dataops/postgres/investigate/request",
    "postgres_result": "dataops/postgres/investigate/result",
    "snowflake_request": "dataops/snowflake/investigate/request",
    "snowflake_result": "dataops/snowflake/investigate/result",
    "incident_resolved": "dataops/incidents/resolved",
    "slack_notification": "dataops/notifications/slack",
}


@dataclass
class EventBus:
    subscribers: dict[str, list[Handler]] = field(default_factory=lambda: defaultdict(list))
    published: list[tuple[str, Message]] = field(default_factory=list)

    def subscribe(self, topic: str, handler: Handler) -> None:
        self.subscribers[topic].append(handler)

    async def publish(self, topic: str, message: Message) -> None:
        self.published.append((topic, message))
        print(f"\nPUBLISH {topic}")
        print(json.dumps(message, indent=2))
        await asyncio.gather(*(handler(topic, message) for handler in self.subscribers[topic]))


class IncidentOrchestrator:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        bus.subscribe(TOPICS["incident_created"], self.handle)

    async def handle(self, _: str, incident: Message) -> None:
        classified = {
            "incident_id": incident["incident_id"],
            "category": "cross-system-dataops",
            "priority": "p1" if incident.get("severity") == "high" else "p2",
            "reason": "Symptoms include live checkout failures and stale analytics data.",
        }
        await self.bus.publish(TOPICS["incident_classified"], classified)

        investigation_context = {
            "incident_id": incident["incident_id"],
            "title": incident["title"],
            "symptoms": incident["symptoms"],
            "correlation_ids": incident["correlation_ids"],
        }
        await asyncio.gather(
            self.bus.publish(TOPICS["postgres_request"], investigation_context),
            self.bus.publish(TOPICS["snowflake_request"], investigation_context),
        )


class MickPostgresAgent:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        bus.subscribe(TOPICS["postgres_request"], self.handle)

    async def handle(self, _: str, request: Message) -> None:
        await asyncio.sleep(0.25)
        result = {
            "incident_id": request["incident_id"],
            "agent": "Mick PostgreSQL Agent",
            "source_repo": "https://github.com/Gyrus-Dev/Mick",
            "findings": [
                "Detected a spike in row lock waits on orders table.",
                "Top slow query is an order insert path waiting on inventory reservation.",
                "No destructive SQL was executed; investigation remained read-only.",
            ],
            "evidence": {
                "database": request["correlation_ids"]["postgres_database"],
                "slow_query_ms": 2870,
                "lock_waits": 184,
                "write_error_rate": "8%",
            },
            "recommendations": [
                "Review the inventory reservation transaction path.",
                "Temporarily reduce checkout worker concurrency if lock waits continue.",
                "Require approval before applying index or transaction changes.",
            ],
        }
        await self.bus.publish(TOPICS["postgres_result"], result)


class FrostySnowflakeAgent:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        bus.subscribe(TOPICS["snowflake_request"], self.handle)

    async def handle(self, _: str, request: Message) -> None:
        await asyncio.sleep(0.3)
        result = {
            "incident_id": request["incident_id"],
            "agent": "Frosty Snowflake Agent",
            "source_repo": "https://github.com/Gyrus-Dev/frosty",
            "findings": [
                "Orders ingestion task is delayed behind the operational write failures.",
                "Warehouse is healthy; no credit spike or queue saturation detected.",
                "Dashboard staleness appears downstream of the PostgreSQL incident.",
            ],
            "evidence": {
                "database": request["correlation_ids"]["snowflake_database"],
                "pipeline": request["correlation_ids"]["pipeline"],
                "pipeline_lag_minutes": 18,
                "warehouse_queue_depth": 0,
            },
            "recommendations": [
                "Do not resize the warehouse; Snowflake is not the bottleneck.",
                "Backfill the orders pipeline after PostgreSQL write health recovers.",
                "Publish a data freshness note to analytics consumers.",
            ],
        }
        await self.bus.publish(TOPICS["snowflake_result"], result)


class IncidentResponseAggregator:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.results: dict[str, dict[str, Message]] = defaultdict(dict)
        bus.subscribe(TOPICS["postgres_result"], self.handle_postgres)
        bus.subscribe(TOPICS["snowflake_result"], self.handle_snowflake)

    async def handle_postgres(self, _: str, result: Message) -> None:
        self.results[result["incident_id"]]["postgres"] = result
        await self.maybe_resolve(result["incident_id"])

    async def handle_snowflake(self, _: str, result: Message) -> None:
        self.results[result["incident_id"]]["snowflake"] = result
        await self.maybe_resolve(result["incident_id"])

    async def maybe_resolve(self, incident_id: str) -> None:
        result_set = self.results[incident_id]
        if {"postgres", "snowflake"} - result_set.keys():
            return

        postgres = result_set["postgres"]
        snowflake = result_set["snowflake"]
        report = {
            "incident_id": incident_id,
            "status": "investigated",
            "root_cause_hypothesis": (
                "Checkout failures are most likely caused by PostgreSQL lock contention "
                "in the order write path. Snowflake dashboard staleness is a downstream symptom."
            ),
            "evidence": {
                "postgres": postgres["evidence"],
                "snowflake": snowflake["evidence"],
            },
            "recommended_actions": [
                "Page the checkout/database owner with PostgreSQL lock evidence.",
                "Pause non-critical checkout workers if lock waits keep rising.",
                "Backfill Snowflake orders pipeline after write health recovers.",
                "Require human approval before executing database-changing remediation.",
            ],
            "executive_summary": (
                "The incident appears operational rather than analytical. PostgreSQL lock "
                "contention is affecting checkout writes, and Snowflake is lagging because "
                "orders are not landing normally upstream."
            ),
        }
        await self.bus.publish(TOPICS["incident_resolved"], report)
        await self.bus.publish(
            TOPICS["slack_notification"],
            {
                "channel": "#dataops-incidents",
                "text": report["executive_summary"],
                "incident_id": incident_id,
            },
        )


def load_events(path: Path | None) -> list[Message]:
    if path is None:
        path = Path(__file__).resolve().parents[2] / "demo" / "sample-incident-events.json"
    with path.open("r", encoding="utf-8") as event_file:
        payload = json.load(event_file)
    if isinstance(payload, dict):
        return [payload]
    return payload


async def run(event_path: Path | None) -> None:
    bus = EventBus()
    IncidentOrchestrator(bus)
    MickPostgresAgent(bus)
    FrostySnowflakeAgent(bus)
    IncidentResponseAggregator(bus)

    for event in load_events(event_path):
        await bus.publish(TOPICS["incident_created"], event)

    print("\nDemo complete. Published topics:")
    for topic, _ in bus.published:
        print(f"- {topic}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local DataOps Agent Mesh demo.")
    parser.add_argument("--event", type=Path, help="Path to a JSON incident event or event list.")
    args = parser.parse_args()
    asyncio.run(run(args.event))


if __name__ == "__main__":
    main()
