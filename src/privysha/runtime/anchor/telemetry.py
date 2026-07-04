import json
import logging
from typing import Dict, Any
from .types import ActionEvent, MemoryEvent, RiskSummary
from .verdicts import ActionVerdict, MemoryVerdict

class AnchorTelemetry:
    """
    Structured telemetry engine for Anchor Runtime.
    Tracks risks, drift, blocked actions, and ensures sensitive data is redacted.
    """
    def __init__(self, log_file: str = "anchor_telemetry.jsonl"):
        self.logger = logging.getLogger("AnchorTelemetry")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(message)s')  # Just output the JSON string
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _redact_payload(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Redacts all values to prevent secret leakage.
        Stores keys to track structure/tool usage without exposing values.
        """
        return {k: "[REDACTED]" for k in payload.keys()}

    def log_action_evaluated(self, action: ActionEvent, verdict: ActionVerdict):
        """
        Logs an evaluated action.
        """
        log_entry = {
            "event_type": "action_evaluated",
            "timestamp": action.timestamp,
            "action_id": action.action_id,
            "action_type": action.action_type,
            "payload_keys": self._redact_payload(action.payload),
            "verdict": verdict.verdict.value,
            "reason": verdict.reason,
            "risk_score": verdict.risk_score
        }
        self.logger.info(json.dumps(log_entry))

    def log_memory_evaluated(self, event: MemoryEvent, verdict: MemoryVerdict):
        """
        Logs an evaluated memory operation.
        """
        log_entry = {
            "event_type": "memory_evaluated",
            "timestamp": event.timestamp,
            "event_id": event.event_id,
            "operation": event.operation,
            "scope": event.scope,
            "content": "[REDACTED_FOR_TELEMETRY]",
            "verdict": verdict.verdict.value,
            "reason": verdict.reason,
            "risk_score": verdict.risk_score
        }
        self.logger.info(json.dumps(log_entry))

    def log_risk_summary(self, summary: RiskSummary, timestamp: float):
        """
        Logs the periodic or session-end risk summary.
        """
        log_entry = {
            "event_type": "risk_summary",
            "timestamp": timestamp,
            "alignment_score": summary.alignment_score,
            "memory_integrity_score": summary.memory_integrity_score,
            "drift_score": summary.drift_score,
            "total_risk_score": summary.total_risk_score,
            "severity": summary.severity.value,
            "explanation": summary.explanation
        }
        self.logger.info(json.dumps(log_entry))
