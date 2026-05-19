# Architecture

## Problem

Production data incidents often span operational databases, analytical warehouses, pipelines, dashboards, and business systems. Traditional incident workflows are slow because each system has its own logs, query surface, runbooks, and owners.

The goal of this demo is to show how an event-driven agent mesh can coordinate specialized agents without turning them into one tightly coupled application.

## Core Idea

Mick and Frosty already contain specialized database intelligence. Solace provides the event-driven coordination layer that lets those agents participate in a larger enterprise workflow.

```text
Incident Event
  -> Orchestrator
  -> PostgreSQL Investigation
  -> Snowflake Investigation
  -> Correlation
  -> Human-Approved Remediation
  -> Notification
```

## Components

| Component | Responsibility |
| --- | --- |
| Incident Producer | Emits operational events from monitoring, ticketing, or app telemetry. |
| Solace Event Broker | Routes incident and agent messages by topic. |
| Agent Mesh Orchestrator | Breaks the incident into tasks and dispatches work to the right agents. |
| Mick Agent | Investigates PostgreSQL symptoms such as slow queries, locks, indexes, and data health. |
| Frosty Agent | Investigates Snowflake symptoms such as pipeline lag, warehouse spend, failed tasks, and data quality. |
| Response Aggregator | Correlates evidence, recommends next actions, and prepares executive and engineering summaries. |
| Approval Gateway | Requires a human event before write operations or risky remediation. |

## Topic Taxonomy

```text
dataops/incidents/created
dataops/incidents/classified
dataops/postgres/investigate/request
dataops/postgres/investigate/result
dataops/snowflake/investigate/request
dataops/snowflake/investigate/result
dataops/remediation/approval/requested
dataops/remediation/approval/received
dataops/incidents/resolved
dataops/notifications/slack
```

## Why This Is Solace-Native

- Producers do not need to know which agents exist.
- Agents do not need to call each other directly.
- The workflow can run asynchronously and tolerate slow systems.
- Topic routing makes the workflow observable and extensible.
- New agents can subscribe to the same business events without changing the producer.

## Demo Boundary

The local demo uses an in-memory event bus to make the story runnable anywhere. The production design replaces that bus with Solace PubSub+ and Solace Agent Mesh gateway/orchestrator configuration.

