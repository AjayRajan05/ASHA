from typing import Tuple, List
from .contracts import MissionContract
from .types import ActionEvent

class AlignmentEvaluator:
    """
    Evaluates current actions against the Mission Contract to calculate an alignment score (0.0 to 1.0).
    """

    def evaluate(self, action: ActionEvent, contract: MissionContract) -> Tuple[float, str]:
        """
        Calculates mission continuity based on multiple relevance dimensions.
        Returns: (score, explanation)
        """
        score = 1.0
        explanations: List[str] = []

        action_type = action.action_type
        
        # 1. Action/Tool Relevance
        if action_type in contract.forbidden_actions:
            score *= 0.0
            explanations.append(f"Action '{action_type}' is explicitly forbidden.")
        elif contract.allowed_tools and action_type not in contract.allowed_tools:
            # If the action is a tool call, but not explicitly allowed
            if action_type == "tool_call":
                tool_name = action.payload.get("tool_name", "")
                if tool_name not in contract.allowed_tools:
                    score *= 0.5
                    explanations.append(f"Tool '{tool_name}' is not in allowed tools list.")
            else:
                score *= 0.8
                explanations.append(f"Action '{action_type}' is not recognized as an allowed tool.")
        
        # 2. Domain & Data Relevance (simulated via payload inspection)
        payload_str = str(action.payload).lower()
        for forbidden in contract.forbidden_actions:
            if forbidden.lower() in payload_str:
                score *= 0.3
                explanations.append(f"Payload contains references to forbidden action/domain '{forbidden}'.")

        # 3. Objective & Side-Effect Relevance
        # If action modifies state significantly and the risk tolerance is LOW
        if any(keyword in action_type for keyword in ["write", "update", "delete", "send"]):
            if contract.risk_tolerance == "LOW":
                score *= 0.7
                explanations.append("State-mutating action encountered under LOW risk tolerance.")
        
        # 4. Continuity check based on payload similarity to goal could be done here.
        # We assume baseline alignment unless penalties apply.
        
        explanation = " | ".join(explanations) if explanations else "Action aligns with mission parameters."
        
        final_score = max(0.0, min(1.0, score))
        return final_score, explanation
