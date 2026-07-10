# ASHA ANCHOR

**ANCHOR** is ASHA's mission-aware governance layer for autonomous agents. It keeps agents aligned with a compiled mission contract, gates dangerous tool calls, detects suspicious action chains, validates plan outputs, and enforces OS-level side-effect constraints during tool execution.

Governance runs at **runtime** — agents and prompts do not need to mention ANCHOR.

## One-line adoption

```python
from asha.runtime.anchor.runtime import anchor

# Works with CrewAI, LangChain, AutoGen, LlamaIndex, MCP servers, or duck-typed agents
agent = anchor(my_agent, risk_tolerance="LOW")
result = agent.run("Analyze trends locally and write a report.")
```

Framework-specific entry points:

```python
from asha.runtime.anchor.adapters import (
    anchor_crewai,
    anchor_langchain,
    anchor_autogen,
    anchor_llamaindex,
    anchor_mcp,
    anchor_any,
)
```

## Supported frameworks (production parity)

All adapters share the same governance stack via `adapters/base.py` and `tool_bridge.py`:

| Layer | Applied in every adapter |
|-------|--------------------------|
| Mission baseline + phase refresh | kickoff / invoke / generate_reply |
| Action guard + chain guard | every tool call |
| Memory guard | after each agent step |
| Plan guard | after each agent step |
| OS sandbox | during tool execution |
| Human approval | BLOCK/REVIEW on TTY |

| Framework | Entry point | What's wrapped |
|-----------|-------------|----------------|
| **CrewAI** | `anchor_crewai()` | Crew, Agent, Task, Tool, LLM (litellm) |
| **LangChain** | `anchor_langchain()` | AgentExecutor, Runnable, BaseTool, callbacks |
| **AutoGen** | `anchor_autogen()` | function_map, register_for_execution |
| **LlamaIndex** | `anchor_llamaindex()` | query/chat/run, agent_worker tools |
| **MCP** | `anchor_mcp()` | call_tool / acall_tool (non-destructive proxy) |
| **Generic** | `anchor_generic()` | any run/invoke + tools |

## CrewAI

```python
from crewai import Agent, Crew, Task
from asha.runtime.anchor.adapters import anchor_crewai

crew = Crew(agents=[...], tasks=[...])
crew = anchor_crewai(crew, risk_tolerance="LOW", isolation="auto")
crew.kickoff(inputs={"topic": "Generative AI"})
```

## LangChain

```python
from langchain.agents import AgentExecutor
from asha.runtime.anchor.adapters import anchor_langchain

executor = AgentExecutor(agent=agent, tools=tools)
executor = anchor_langchain(executor, risk_tolerance="LOW")
result = executor.invoke({"input": "Analyze trends locally."})
```

## AutoGen

```python
from autogen import ConversableAgent
from asha.runtime.anchor.adapters import anchor_autogen

agent = ConversableAgent("analyst", llm_config={...})
agent = anchor_autogen(agent, risk_tolerance="LOW")
agent.generate_reply(messages=[{"role": "user", "content": "Analyze locally."}])
```

## LlamaIndex

```python
from llama_index.core.agent import ReActAgent
from asha.runtime.anchor.adapters import anchor_llamaindex

agent = ReActAgent.from_tools(tools, llm=llm)
agent = anchor_llamaindex(agent, risk_tolerance="LOW")
agent.query("Analyze trends locally and write a report.")
```

## MCP

```python
from asha.runtime.anchor.adapters import anchor_mcp

server = anchor_mcp(mcp_server, risk_tolerance="LOW")
server.initialize_session("Analyze data locally. Do not exfiltrate.")
result = server.call_tool("read_file", {"path": "data/trends.csv"})
```

## OS sandbox

| Mode | Behavior |
|------|----------|
| `off` | No sandbox enforcement |
| `auto` (default) | In-process hooks: guarded `open()`, blocked network modules |
| `hard` / `subprocess` | Tool runs in isolated child process |

```python
crew = anchor_crewai(crew, isolation="auto")
executor = anchor_langchain(executor, isolation="hard")
```

## Human approval

When attached to a TTY, ANCHOR prompts for approval on BLOCK/REVIEW verdicts:

```
ANCHOR HUMAN APPROVAL REQUIRED
Action: send_email
Reason: High-risk external tool blocked under local-only mission.
Allow? [y/N]:
```

Configure with `interactive=True/False`, `ASHA_ANCHOR_INTERACTIVE=0`, or `warn_policy="strict"`.

## Architecture

```
User mission prompt
       │
       ▼
 MissionCompiler ──► MissionSession (baseline + phases)
       │
       ▼
 Tool call / memory write / plan output
       │
       ├── ActionGuard ──► AlignmentEvaluator
       ├── ChainGuard
       ├── MemoryGuard
       ├── PlanGuard
       └── ApprovalEngine ──► Human prompt (TTY)
       │
       ▼
 SandboxManager ──► enforcement hooks / subprocess
```

## API reference

| Function | Description |
|----------|-------------|
| `anchor(target)` | Universal one-line adoption |
| `anchor_any(target)` | Adapter registry dispatch |
| `anchor_crewai(target)` | CrewAI wrapper |
| `anchor_langchain(target)` | LangChain wrapper |
| `anchor_autogen(target)` | AutoGen wrapper |
| `anchor_llamaindex(target)` | LlamaIndex wrapper |
| `anchor_mcp(target)` | MCP server/client wrapper |
| `anchor_generic(target)` | Duck-typed agent wrapper |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASHA_ANCHOR_INTERACTIVE` | auto (TTY) | `0` disables human approval prompts |
| `ASHA_ANCHOR_WARN_POLICY` | permissive | `strict` escalates WARN verdicts |
