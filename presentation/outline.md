# Presentation Outline

## 1. Introduction

Title: Event-Driven DataOps With Solace Agent Mesh

Introduce the demo as an extension of two existing open-source projects:

- Mick: PostgreSQL agent.
- Frosty: Snowflake agent.

## 2. Problem Overview

Production incidents often cross operational and analytical systems.

Common pain points:

- Teams manually jump between dashboards, databases, logs, and tickets.
- AI agents are useful, but isolated agents become another integration burden.
- Enterprises need governance, async workflows, auditability, and human approval.

## 3. Architecture With Solace

Show the architecture diagram from `architecture.md`.

Core message:

Solace acts as the event-driven nervous system. Agent Mesh performs orchestration. Mick and Frosty remain specialized database agents.

## 4. Workflow

Incident event:

```text
dataops/incidents/created
```

Agent fan-out:

```text
dataops/postgres/investigate/request
dataops/snowflake/investigate/request
```

Final result:

```text
dataops/incidents/resolved
```

## 5. Advantages Of Using Solace

- Decoupled producers and agents.
- Asynchronous processing for slow investigations.
- Topic-level observability.
- Gateway-based access control.
- Easy extension to more agents and interfaces.
- Production path from local demo to cloud event mesh.

## 6. Demo

Run the local simulation.

Talk track:

- This local in-memory bus mirrors the Solace topic contract.
- The same messages become PubSub+ topic messages in the Solace Cloud version.
- Mick and Frosty are invoked through adapter boundaries.

## 7. Production Hardening

Next steps:

- Solace Cloud broker.
- Agent Mesh project configuration.
- REST gateway for incident submission.
- Queue subscriptions per agent.
- Approval workflow for write actions.
- Observability dashboard.

## 8. Q&A

Likely questions:

- Why use events instead of direct API calls?
- How do you avoid unsafe database changes?
- How would you deploy this in production?
- What parts are live versus mocked?
- How would this scale to more systems?

