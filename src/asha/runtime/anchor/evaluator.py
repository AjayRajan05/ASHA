from typing import Tuple, List
from .contracts import MissionContract
from .types import ActionEvent
from .payload_inspection import (
    extract_inspection_metadata,
    find_forbidden_metadata_matches,
    format_forbidden_matches,
    is_high_risk_tool,
    is_mission_local_tool,
    tool_name_policy_violations,
    validate_resource_scope,
)

class AlignmentEvaluator:
    """
    Evaluates current actions against the Mission Contract to calculate an alignment score (0.0 to 1.0).
    """

    def evaluate(self, action: ActionEvent, contract: MissionContract) -> Tuple[float, str, List[str]]:
        """
        Calculates mission continuity based on multiple relevance dimensions.
        Returns: (score, explanation, risk_triggers)
        """
        score = 1.0
        explanations: List[str] = []
        triggers: List[str] = []

        action_type = action.action_type
        tool_name = str(action.payload.get("tool_name", "")) if action_type == "tool_call" else ""

        # 0. High-risk / exfiltration tools under local-only missions
        if action_type == "tool_call" and tool_name:
            if contract.local_only or contract.forbid_network_exfiltration:
                if is_high_risk_tool(tool_name) and not is_mission_local_tool(tool_name, contract):
                    score = 0.0
                    msg = (
                        f"Tool '{tool_name}' performs external or destructive side-effects "
                        "and is blocked under the current mission scope."
                    )
                    explanations.append(msg)
                    triggers.append(msg)

            name_violations = tool_name_policy_violations(tool_name, contract.forbidden_actions)
            if name_violations and not is_mission_local_tool(tool_name, contract):
                score = 0.0
                detail = ", ".join(name_violations)
                msg = f"Tool '{tool_name}' matches forbidden capability token(s): {detail}."
                explanations.append(msg)
                triggers.append(msg)
        
        # 1. Action/Tool Relevance
        if action_type in contract.forbidden_actions:
            score = 0.0
            msg = f"Action '{action_type}' is explicitly forbidden."
            explanations.append(msg)
            triggers.append(msg)
        elif tool_name and tool_name in contract.forbidden_actions:
            score = 0.0
            msg = f"Tool '{tool_name}' is explicitly forbidden."
            explanations.append(msg)
            triggers.append(msg)
        elif contract.allowed_tools and action_type not in contract.allowed_tools:
            if action_type == "tool_call":
                if tool_name not in contract.allowed_tools:
                    score = 0.0
                    msg = f"Tool '{tool_name}' is not in allowed tools list."
                    explanations.append(msg)
                    triggers.append(msg)
            else:
                score *= 0.8
                explanations.append(f"Action '{action_type}' is not recognized as an allowed tool.")
        
        metadata = extract_inspection_metadata(action.payload)

        # 2. Resource-scoped read/write permissions
        if action_type == "tool_call" and tool_name:
            scope_violation = validate_resource_scope(tool_name, metadata, contract)
            if scope_violation is not None:
                score = 0.0
                msg = (
                    f"Resource scope violation: {scope_violation.term} on "
                    f"{scope_violation.field}='{scope_violation.value}'"
                )
                explanations.append(msg)
                triggers.append(msg)

        # 3. Domain & policy relevance (structured metadata only)
        if action_type == "tool_call":
            forbidden_matches = find_forbidden_metadata_matches(
                metadata,
                contract.forbidden_actions,
                network_only_tokens=contract.forbidden_network_tokens
                if contract.forbid_network_exfiltration
                else None,
            )
        else:
            forbidden_matches = find_forbidden_metadata_matches(
                {"payload": str(action.payload)},
                contract.forbidden_actions,
            )

        if forbidden_matches:
            score *= 0.3 ** len(forbidden_matches)
            detail = format_forbidden_matches(forbidden_matches)
            explanations.append("Metadata policy violations: " + "; ".join(detail))
            triggers.extend(detail)

        # 4. Objective & Side-Effect Relevance
        if any(keyword in action_type for keyword in ["write", "update", "delete", "send"]):
            if contract.risk_tolerance == "LOW":
                score *= 0.7
                explanations.append("State-mutating action encountered under LOW risk tolerance.")
        elif (
            action_type == "tool_call"
            and tool_name
            and "write" in tool_name.lower()
            and tool_name in contract.allowed_tools
            and "write" in contract.allowed_actions
        ):
            pass
        elif (
            action_type == "tool_call"
            and tool_name
            and any(keyword in tool_name.lower() for keyword in ["write", "update", "delete", "send"])
            and contract.risk_tolerance == "LOW"
        ):
            score *= 0.7
            explanations.append("State-mutating tool encountered under LOW risk tolerance.")
        
        explanation = " | ".join(explanations) if explanations else "Action aligns with mission parameters."
        
        final_score = max(0.0, min(1.0, score))
        return final_score, explanation, triggers
