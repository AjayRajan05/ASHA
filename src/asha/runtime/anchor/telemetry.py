import json
import logging
from typing import Any, Dict, Optional

from .types import ActionEvent, ChainEvent, MemoryEvent, RiskSummary, AnchorState
from .verdicts import ActionVerdict, ChainVerdict, MemoryVerdict
from .plan_guard import PlanVerdict


class AnchorTelemetry:
    """
    Structured telemetry engine for Anchor Runtime.
    Tracks risks, drift, blocked actions, and ensures sensitive data is redacted.
    """

    def __init__(self, log_file: str = "anchor_telemetry.jsonl"):
        self.log_file = log_file
        self.logger = logging.getLogger(f"AnchorTelemetry.{log_file}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _emit(self, log_entry: Dict[str, Any]) -> None:
        self.logger.info(json.dumps(log_entry))

    def _redact_payload(self, payload: Dict[str, Any]) -> Dict[str, str]:
        return {k: "[REDACTED]" for k in payload.keys()}

    def log_action_evaluated(self, action: ActionEvent, verdict: ActionVerdict) -> None:
        self._emit(
            {
                "event_type": "action_evaluated",
                "timestamp": action.timestamp,
                "action_id": action.action_id,
                "action_type": action.action_type,
                "payload_keys": self._redact_payload(action.payload),
                "verdict": verdict.verdict.value,
                "reason": verdict.reason,
                "risk_score": verdict.risk_score,
                "risk_triggers": list(verdict.risk_triggers),
            }
        )

    def log_memory_evaluated(self, event: MemoryEvent, verdict: MemoryVerdict) -> None:
        self._emit(
            {
                "event_type": "memory_evaluated",
                "timestamp": event.timestamp,
                "event_id": event.event_id,
                "operation": event.operation,
                "scope": event.scope,
                "content": "[REDACTED_FOR_TELEMETRY]",
                "verdict": verdict.verdict.value,
                "reason": verdict.reason,
                "risk_score": verdict.risk_score,
            }
        )

    def log_chain_evaluated(self, chain_event: ChainEvent, verdict: ChainVerdict) -> None:
        self._emit(
            {
                "event_type": "chain_evaluated",
                "timestamp": chain_event.timestamp,
                "chain_id": chain_event.chain_id,
                "pattern_detected": chain_event.pattern_detected,
                "action_count": len(chain_event.actions),
                "verdict": verdict.verdict.value,
                "reason": verdict.reason,
                "risk_score": verdict.risk_score,
            }
        )

    def log_plan_evaluated(self, verdict: PlanVerdict, *, target_id: str, timestamp: float) -> None:
        self._emit(
            {
                "event_type": "plan_evaluated",
                "timestamp": timestamp,
                "target_id": target_id,
                "verdict": verdict.verdict.value,
                "reason": verdict.reason,
                "risk_score": verdict.risk_score,
            }
        )

    def log_approval(self, record_id: str, target_id: str, verdict: str, reason: str, timestamp: float) -> None:
        self._emit(
            {
                "event_type": "approval_recorded",
                "timestamp": timestamp,
                "record_id": record_id,
                "target_id": target_id,
                "verdict": verdict,
                "reason": reason,
            }
        )

    def log_risk_summary(self, summary: RiskSummary, timestamp: float) -> None:
        self._emit(
            {
                "event_type": "risk_summary",
                "timestamp": timestamp,
                "alignment_score": summary.alignment_score,
                "memory_integrity_score": summary.memory_integrity_score,
                "drift_score": summary.drift_score,
                "total_risk_score": summary.total_risk_score,
                "severity": summary.severity.value,
                "explanation": summary.explanation,
            }
        )

    def log_session_finalized(self, summary: RiskSummary, state: AnchorState, timestamp: float) -> None:
        self._emit(
            {
                "event_type": "session_finalized",
                "timestamp": timestamp,
                "mission_id": state.mission.mission_id if state.mission else None,
                "tools_used": list(state.tools_used),
                "action_count": len(state.actions_history),
                "memory_events": len(state.memory_history),
                "total_risk_score": summary.total_risk_score,
                "severity": summary.severity.value,
            }
        )
