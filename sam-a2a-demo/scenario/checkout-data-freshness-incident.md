# Checkout Data Freshness Incident Prompt

Use this prompt with `sam task run`:

```text
We have a production checkout analytics incident. The application is processing successful payments, but the executive Snowflake orders dashboard is stale by 18 minutes and the ops team sees missing recent orders. Coordinate the investigation through the available agents. I need a concise incident report with likely root cause, what evidence to collect in Snowflake, freshness checks to run, safe remediation steps, and follow-up prevention work.
```

What this demonstrates:

- Gyrus/Frosty is exposed locally as a standard A2A HTTP agent.
- Solace Agent Mesh discovers the proxied `GyrusDataOps` agent through the A2A proxy.
- The orchestrator delegates database and analytics diagnostics over the event mesh.
- The final answer is synthesized as a realistic DataOps incident response.
