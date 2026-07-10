import uuid
import time
from typing import Any, Dict
from .verdicts import ActionVerdict, Verdict
from .types import ActionEvent
from .contracts import MissionContract
from .evaluator import AlignmentEvaluator
from .payload_inspection import is_high_risk_tool, is_mission_local_tool

class ActionGuard:
    """
    The enforcement gate for all runtime actions.
    Intercepts, normalizes, and evaluates actions against the Mission Contract.
    """
    def __init__(self, evaluator: AlignmentEvaluator):
        self.evaluator = evaluator
        
    def normalize_action(self, action_type: str, payload: Dict[str, Any]) -> ActionEvent:
        """
        Normalizes any intercepted action into a structured ActionEvent.
        """
        return ActionEvent(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            payload=payload,
            timestamp=time.time()
        )

    def evaluate_action(self, action: ActionEvent, contract: MissionContract) -> ActionVerdict:
        """
        Evaluates the structured action and returns an ActionVerdict.
        """
        score, explanation, triggers = self.evaluator.evaluate(action, contract)
        
        if score >= 0.8:
            verdict = Verdict.ALLOW
        elif score >= 0.5:
            verdict = Verdict.WARN
        elif score >= 0.3:
            verdict = Verdict.REVIEW
        else:
            verdict = Verdict.BLOCK
            
        # Invert score for risk representation (1.0 alignment -> 0.0 risk)
        risk_score = 1.0 - score
        
        # Explicit override for forbidden action types
        if action.action_type in contract.forbidden_actions:
            verdict = Verdict.BLOCK
            risk_score = 1.0
            explanation = f"Action '{action.action_type}' explicitly forbidden by mission contract."

        # High-risk tools always escalate to BLOCK for human approval under local missions
        if action.action_type == "tool_call":
            tool_name = str(action.payload.get("tool_name", ""))
            if tool_name and (contract.local_only or contract.forbid_network_exfiltration):
                if is_high_risk_tool(tool_name) and not is_mission_local_tool(tool_name, contract):
                    verdict = Verdict.BLOCK
                    risk_score = 1.0
                    explanation = (
                        f"High-risk tool '{tool_name}' requires human approval before execution."
                    )

        return ActionVerdict(
            verdict=verdict,
            reason=explanation,
            risk_score=risk_score,
            risk_triggers=tuple(triggers),
        )
