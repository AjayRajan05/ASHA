import time
from typing import Any, Dict, Optional
from .types import AnchorState, RiskSummary
from .verdicts import Verdict, RiskSeverity
from .mission import MissionCompiler
from .evaluator import AlignmentEvaluator
from .action_guard import ActionGuard
from .memory_guard import MemoryGuard
from .chain_guard import ChainGuard
from .approval import ApprovalEngine
from .telemetry import AnchorTelemetry

class AnchorRuntime:
    """
    Central runtime controller for the Anchor subsystem.
    Enforces mission alignment and intercepts all executions.
    """
    def __init__(self, risk_tolerance: str = "LOW"):
        self.state = AnchorState()
        self.mission_compiler = MissionCompiler(default_risk_tolerance=risk_tolerance)
        self.evaluator = AlignmentEvaluator()
        self.action_guard = ActionGuard(self.evaluator)
        self.memory_guard = MemoryGuard()
        self.chain_guard = ChainGuard()
        self.approval_engine = ApprovalEngine()
        self.telemetry = AnchorTelemetry()

    def initialize_mission(self, prompt: str, context: Optional[Dict[str, Any]] = None):
        """Creates the immutable Mission Contract for the session."""
        if self.state.mission is None:
            self.state.mission = self.mission_compiler.compile(prompt, context)

    def _update_risk_summary(self):
        """Calculates and updates the cumulative runtime risk score."""
        if not self.state.mission:
            return

        # 1. Action Alignment
        avg_alignment = 1.0
        if self.state.alignment_history:
            avg_alignment = sum(self.state.alignment_history) / len(self.state.alignment_history)
            
        # 2. Mission Drift Score
        mission_drift = 1.0 - avg_alignment

        # 3. Intent Drift Score (heuristically based on chained drift)
        # Compare current objective to original objective (approximated here by chain history divergence)
        intent_drift = 0.0
        if self.state.actions_history:
            off_task_actions = sum(1 for a in self.state.actions_history if self.state.mission.allowed_tools and a.action_type not in self.state.mission.allowed_tools)
            intent_drift = min(1.0, off_task_actions / max(len(self.state.actions_history), 1))
            
        # Total drift combines mission alignment drift and intent deviation
        drift_score = (mission_drift + intent_drift) / 2.0

        # 4. Memory Integrity Score
        memory_integrity_score = 1.0
        if self.state.memory_history:
            # Writes reduce integrity faster if outside session scope
            high_risk_writes = sum(1 for m in self.state.memory_history if m.operation in ["write", "update"] and m.scope != "session")
            total_writes = sum(1 for m in self.state.memory_history if m.operation in ["write", "update"])
            # Penalty for high risk writes
            if total_writes > 0:
                memory_integrity_score = max(0.0, 1.0 - (high_risk_writes * 0.2))

        # 5. Total Risk Score
        total_risk = (drift_score * 0.6) + ((1.0 - memory_integrity_score) * 0.4)
        total_risk_scaled = total_risk * 100.0

        if total_risk_scaled > 80:
            severity = RiskSeverity.CRITICAL
        elif total_risk_scaled > 50:
            severity = RiskSeverity.HIGH
        elif total_risk_scaled > 20:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        summary = RiskSummary(
            alignment_score=avg_alignment,
            memory_integrity_score=memory_integrity_score,
            drift_score=drift_score,
            total_risk_score=total_risk_scaled,
            severity=severity,
            explanation=f"Cumulative risk calculated. Drift: {drift_score:.2f}"
        )
        self.state.risk_history.append(summary)
        self.telemetry.log_risk_summary(summary, time.time())

    def evaluate_action_request(self, action_type: str, payload: Dict[str, Any]) -> bool:
        """
        Intercepts an action, routes it through guards, handles approvals.
        Returns True if allowed to execute, False otherwise.
        """
        if not self.state.mission:
            return False

        # Normalize
        action = self.action_guard.normalize_action(action_type, payload)
        self.state.actions_history.append(action)

        # 1. Evaluate individual action
        action_verdict = self.action_guard.evaluate_action(action, self.state.mission)
        self.telemetry.log_action_evaluated(action, action_verdict)
        self.state.alignment_history.append(1.0 - action_verdict.risk_score)

        # Process approval
        approval_record = self.approval_engine.process_verdict(action_verdict.verdict, action_verdict.reason, action.action_id)
        self.state.approval_history.append(approval_record)
        
        if approval_record.verdict.verdict == Verdict.BLOCK:
            self._update_risk_summary()
            return False

        # 2. Evaluate action chain
        chain_verdict = self.chain_guard.evaluate_chain(self.state.actions_history, self.state.mission)
        if chain_verdict.verdict in [Verdict.BLOCK, Verdict.REVIEW]:
            chain_approval = self.approval_engine.process_verdict(chain_verdict.verdict, chain_verdict.reason, action.action_id)
            self.state.approval_history.append(chain_approval)
            if chain_approval.verdict.verdict == Verdict.BLOCK:
                self._update_risk_summary()
                return False

        self._update_risk_summary()
        return True

    def evaluate_memory_request(self, operation: str, content: str, scope: str) -> bool:
        """
        Intercepts a memory read/write.
        Returns True if allowed, False otherwise.
        """
        if not self.state.mission:
            return False

        event = self.memory_guard.normalize_memory_event(operation, content, scope)
        self.state.memory_history.append(event)

        memory_verdict = self.memory_guard.evaluate_memory(event, self.state.mission, content)
        self.telemetry.log_memory_evaluated(event, memory_verdict)

        approval_record = self.approval_engine.process_verdict(memory_verdict.verdict, memory_verdict.reason, event.event_id)
        self.state.approval_history.append(approval_record)

        self._update_risk_summary()
        return approval_record.verdict.verdict != Verdict.BLOCK

import contextvars
from typing import Any, Dict, Optional

# Context variable to hold the active runtime session
current_anchor_runtime = contextvars.ContextVar('current_anchor_runtime', default=None)

def anchor(agent: Any) -> Any:
    """
    Public API to wrap an agent with the Anchor Runtime.
    """
    runtime = AnchorRuntime()
    return AnchorWrapper(agent, runtime)

class AnchorWrapper:
    """
    Proxy wrapper that attaches the AnchorRuntime to an Agent.
    """
    def __init__(self, wrapped_agent, anchor_runtime):
        self._wrapped_agent = wrapped_agent
        self._anchor_runtime = anchor_runtime
        self._wrapped_agent._anchor_runtime = anchor_runtime

    def __getattr__(self, name):
        return getattr(self._wrapped_agent, name)

    def run(self, *args, **kwargs):
        prompt = kwargs.get("prompt")
        if not prompt and len(args) > 0:
            prompt = args[0]
            
        if prompt:
            available_tools = []
            if hasattr(self._wrapped_agent, "tools"):
                tools = getattr(self._wrapped_agent, "tools")
                if tools:
                    for t in tools:
                        available_tools.append(t if isinstance(t, str) else getattr(t, "name", str(t)))

            self._anchor_runtime.initialize_mission(prompt, context={"available_tools": available_tools})
            
        # Set the runtime in the context so deep wrappers can find it
        token = current_anchor_runtime.set(self._anchor_runtime)
        try:
            return self._wrapped_agent.run(*args, **kwargs)
        finally:
            current_anchor_runtime.reset(token)
