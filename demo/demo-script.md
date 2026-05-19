# Demo Script

## Opening

Today I am showing an event-driven DataOps workflow built around Solace Agent Mesh. The goal is to coordinate existing specialist agents across PostgreSQL and Snowflake during a production incident.

I already have two open-source database agents:

- Mick for PostgreSQL operations.
- Frosty for Snowflake operations.

The Solace-specific idea is to stop treating these as isolated CLIs and instead place them behind an event-driven agent mesh.

## Step 1: Trigger The Incident

Run:

```bash
python3 src/dataops_mesh_demo/demo.py
```

Explain:

The monitoring system publishes a checkout incident to `dataops/incidents/created`. The producer does not know which agents will handle it.

## Step 2: Orchestration

Point out:

- The orchestrator receives the incident.
- It classifies the incident as a cross-system DataOps problem.
- It fans out investigation requests to PostgreSQL and Snowflake topics.

## Step 3: Mick Investigates PostgreSQL

Explain:

Mick checks operational database signals: slow queries, locks, indexes, table health, and recent write errors. In a full integration, this is where Mick's existing PostgreSQL agent stack is invoked.

## Step 4: Frosty Investigates Snowflake

Explain:

Frosty checks analytical platform signals: failed ingestion tasks, warehouse pressure, pipeline freshness, and data quality. In the demo, the adapter is mocked so the flow is reliable, but the integration boundary maps directly to Frosty's Snowflake agent capabilities.

## Step 5: Aggregate And Recommend

Explain:

The response agent waits for both result events, correlates evidence, and publishes a final incident response. The recommendation keeps write operations behind a human approval step.

## Close

The important point is not that Solace replaces Mick or Frosty. Solace lets them operate as governed, event-driven enterprise agents that can be composed into production workflows.

