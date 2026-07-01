import uuid
import time
from typing import List, Optional
from .verdicts import ChainVerdict, Verdict
from .types import ActionEvent, ChainEvent
from .contracts import MissionContract

class ChainGuard:
    """
    Chain analysis engine to detect malicious multi-step action sequences.
    """
    def __init__(self):
        # Define abstract sequence patterns for detection
        self.suspicious_patterns = [
            ("exfiltration", ["read", "compress", "network"]),
            ("recon_to_escalation", ["list", "read", "shell"]),
            ("prompt_injection_execution", ["webpage", "instruction", "modify"])
        ]

    def normalize_chain(self, actions: List[ActionEvent], pattern: Optional[str] = None) -> ChainEvent:
        """
        Normalizes a detected sequence into a structured ChainEvent.
        """
        return ChainEvent(
            chain_id=str(uuid.uuid4()),
            actions=actions,
            pattern_detected=pattern,
            timestamp=time.time()
        )

    def evaluate_chain(self, history: List[ActionEvent], contract: MissionContract) -> ChainVerdict:
        """
        Analyzes the action history for suspicious cumulative patterns and drift.
        """
        if len(history) < 2:
            return ChainVerdict(Verdict.ALLOW, "Insufficient history for chain analysis.", 0.0)

        # Look at the last 5 actions for immediate chains
        recent_actions = history[-5:]
        action_summary = " ".join([f"{a.action_type} {str(a.payload)}" for a in recent_actions]).lower()

        # 1. Pattern matching for malicious sequences
        for pattern_name, keywords in self.suspicious_patterns:
            match = True
            last_idx = -1
            for kw in keywords:
                idx = action_summary.find(kw, last_idx + 1)
                if idx == -1:
                    match = False
                    break
                last_idx = idx

            if match:
                verdict = Verdict.BLOCK
                reason = f"Detected malicious chain pattern: {pattern_name}"
                risk_score = 1.0
                
                # If risk tolerance is higher, escalate to REVIEW instead of hard BLOCK
                if contract.risk_tolerance in ["HIGH", "CRITICAL"]:
                    verdict = Verdict.REVIEW
                    risk_score = 0.8
                
                return ChainVerdict(verdict, reason, risk_score)

        # 2. Mission drift detection across chain
        # If multiple recent actions stray from explicitly allowed tools
        if contract.allowed_tools:
            drift_count = sum(1 for a in recent_actions if a.action_type not in contract.allowed_tools and a.action_type != "tool_call")
            if drift_count >= 3:
                return ChainVerdict(Verdict.WARN, "Chain shows cumulative signs of mission drift.", 0.6)

        return ChainVerdict(Verdict.ALLOW, "No malicious chains detected.", 0.0)
