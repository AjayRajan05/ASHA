"""Chain guard with tool-name sequence detection."""

from __future__ import annotations

import uuid
import time
from typing import List, Optional, Sequence, Tuple

from .verdicts import ChainVerdict, Verdict
from .types import ActionEvent, ChainEvent
from .contracts import MissionContract
from .payload_inspection import is_high_risk_tool, is_read_tool


# Tool-name suffix/prefix patterns for multi-step attack detection
_SUSPICIOUS_TOOL_SEQUENCES: Tuple[Tuple[Sequence[str], Sequence[str], str], ...] = (
    (("load_", "read_", "fetch_"), ("send_", "upload_", "network_"), "read_to_exfil"),
    (("load_", "read_"), ("send_email", "upload_to_cloud"), "local_read_to_external"),
    (("write_",), ("delete_", "remove_"), "write_then_destroy"),
)

# Legacy keyword patterns (non-tool actions)
_KEYWORD_PATTERNS = (
    ("exfiltration", ["read", "compress", "network"]),
    ("recon_to_escalation", ["list", "read", "shell"]),
)


class ChainGuard:
    """Chain analysis engine to detect malicious multi-step action sequences."""

    def normalize_chain(self, actions: List[ActionEvent], pattern: Optional[str] = None) -> ChainEvent:
        return ChainEvent(
            chain_id=str(uuid.uuid4()),
            actions=actions,
            pattern_detected=pattern,
            timestamp=time.time(),
        )

    @staticmethod
    def _tool_names(history: List[ActionEvent]) -> List[str]:
        names: List[str] = []
        for action in history:
            if action.action_type != "tool_call":
                continue
            name = str(action.payload.get("tool_name", "") or "")
            if name:
                names.append(name)
        return names

    @staticmethod
    def _matches_prefix(name: str, prefixes: Sequence[str]) -> bool:
        lowered = name.lower()
        return any(lowered.startswith(prefix) or prefix.rstrip("_") in lowered for prefix in prefixes)

    def _detect_tool_sequence(self, tool_names: List[str]) -> Optional[str]:
        if len(tool_names) < 2:
            return None
        recent = tool_names[-5:]
        for read_prefixes, exfil_prefixes, pattern_name in _SUSPICIOUS_TOOL_SEQUENCES:
            read_idx = next(
                (i for i, name in enumerate(recent) if self._matches_prefix(name, read_prefixes)),
                None,
            )
            exfil_idx = next(
                (
                    i
                    for i, name in enumerate(recent)
                    if self._matches_prefix(name, exfil_prefixes) or is_high_risk_tool(name)
                ),
                None,
            )
            if read_idx is not None and exfil_idx is not None and exfil_idx > read_idx:
                return pattern_name
        return None

    def evaluate_chain(self, history: List[ActionEvent], contract: MissionContract) -> ChainVerdict:
        if len(history) < 2:
            return ChainVerdict(Verdict.ALLOW, "Insufficient history for chain analysis.", 0.0)

        tool_names = self._tool_names(history)
        sequence = self._detect_tool_sequence(tool_names)
        if sequence:
            verdict = Verdict.BLOCK
            reason = f"Detected suspicious tool chain: {sequence}"
            risk_score = 1.0
            if contract.risk_tolerance in ["HIGH", "CRITICAL"]:
                verdict = Verdict.REVIEW
                risk_score = 0.85
            return ChainVerdict(verdict, reason, risk_score)

        # Local read followed by high-risk tool under local-only mission
        if contract.local_only and len(tool_names) >= 2:
            if any(is_read_tool(name) for name in tool_names[:-1]) and is_high_risk_tool(tool_names[-1]):
                return ChainVerdict(
                    Verdict.BLOCK,
                    "Local data access followed by high-risk external tool.",
                    1.0,
                )

        recent_actions = history[-5:]
        action_summary = " ".join(
            f"{a.action_type} {str(a.payload)}" for a in recent_actions
        ).lower()

        for pattern_name, keywords in _KEYWORD_PATTERNS:
            match = True
            last_idx = -1
            for kw in keywords:
                idx = action_summary.find(kw, last_idx + 1)
                if idx == -1:
                    match = False
                    break
                last_idx = idx
            if match:
                verdict = Verdict.BLOCK if contract.risk_tolerance not in ["HIGH", "CRITICAL"] else Verdict.REVIEW
                return ChainVerdict(
                    verdict,
                    f"Detected malicious chain pattern: {pattern_name}",
                    1.0 if verdict == Verdict.BLOCK else 0.8,
                )

        return ChainVerdict(Verdict.ALLOW, "No malicious chains detected.", 0.0)
