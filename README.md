# Event-Driven DataOps Agent Mesh

This demo shows how Solace Agent Mesh can orchestrate existing database agents across operational and analytical systems during a production incident.

It builds on two open-source projects:

- [Mick](https://github.com/Gyrus-Dev/Mick): autonomous PostgreSQL agent for operational data systems.
- [Frosty](https://github.com/Gyrus-Dev/frosty): autonomous Snowflake agent for analytical data systems.

The demo scenario is a checkout incident. A monitoring system publishes an incident event, Solace routes it through an event-driven agent mesh, Mick investigates PostgreSQL, Frosty investigates Snowflake, and a response agent produces a human-readable incident report with recommended next actions.

## Why Solace

Solace is the coordination layer between systems and agents:

- Events are routed by business topic instead of direct service calls.
- Mick and Frosty remain independently deployable agents.
- Additional agents can be added without changing incident producers.
- Human approval gates can be modeled as event-driven workflow steps.
- The same architecture can support REST, Slack, Teams, MQTT, and application events through Solace gateways.

## Demo Architecture

```text
Monitoring System / REST Gateway
          |
          v
dataops/incidents/created
          |
          v
Solace Event Broker + Agent Mesh Orchestrator
     /                                 \
    v                                   v
Mick PostgreSQL Agent              Frosty Snowflake Agent
    |                                   |
    v                                   v
dataops/postgres/investigate/result  dataops/snowflake/investigate/result
     \                                 /
      v                               v
       Incident Response Aggregator Agent
                  |
                  v
        dataops/incidents/resolved
                  |
                  v
       Dashboard / Slack / Ticket Update
```

## Run The Local Simulation

The first version is dependency-free and simulates the event-driven workflow locally. This keeps the interview demo reliable while the Solace Cloud and Agent Mesh configuration are being finalized.

```bash
python3 src/dataops_mesh_demo/demo.py
```

To run a specific sample event:

```bash
python3 src/dataops_mesh_demo/demo.py --event demo/sample-incident-events.json
```

## Demo Flow

1. Publish a checkout latency incident.
2. The orchestrator fans out investigation tasks.
3. Mick returns PostgreSQL findings.
4. Frosty returns Snowflake findings.
5. The response agent correlates evidence and recommends next actions.
6. A final incident report is published to the resolved topic.

## Repository Layout

```text
configs/
  agent-mesh/       Solace Agent Mesh-style component definitions
  solace/           Topic taxonomy and broker notes
demo/
  demo-script.md    Spoken runbook for the interview demo
  sample-incident-events.json
presentation/
  outline.md        Slide-by-slide presentation narrative
src/
  dataops_mesh_demo/
    demo.py         Local event-driven simulation
```

## Next Integration Steps

1. Replace the in-memory event bus with Solace PubSub+ topics.
2. Wrap Mick as an Agent Mesh tool/agent endpoint.
3. Wrap Frosty as an Agent Mesh tool/agent endpoint.
4. Add a REST or web gateway for incident submission.
5. Add an approval topic before executing write operations.

