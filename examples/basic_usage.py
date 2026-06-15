#!/usr/bin/env python3
"""Basic Agent usage (v0.4.1). No API keys — uses mock adapter."""

from privysha import Agent

agent = Agent(model="mock", privacy=True, token_budget=1200)

query = "Hey bro can you analyze this dataset for anomalies with john@example.com?"

# Default: returns response string
response = agent.run(query)
print("Response:", response)

# With trace: returns AgentResult
result = agent.run(query, trace=True)
print("Processed:", result.output)
print("LLM reply :", result.response)
