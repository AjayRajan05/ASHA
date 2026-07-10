import time
import uuid
from typing import Dict, Any, List
from .contracts import MissionContract
from .intent_parser import parse_mission_intent

class MissionCompiler:
    """
    Compiles a user prompt and task context into an immutable MissionContract.
    """
    def __init__(self, default_risk_tolerance: str = "LOW"):
        self.default_risk_tolerance = default_risk_tolerance

    def compile(self, prompt: str, context: Dict[str, Any] = None) -> MissionContract:
        """
        Extracts the primary goal, domains, and actions from the user prompt.
        Prioritizes the explicit goal, derives scope conservatively, and is deterministic.
        """
        if context is None:
            context = {}

        goal = prompt.strip()
        intent = parse_mission_intent(prompt, context)
        intent_summary = (
            f"User explicitly requested: {goal} | "
            f"local_only={intent.local_only} | "
            f"forbid_network_exfiltration={intent.forbid_network_exfiltration}"
        )

        allowed_actions = ["read", "list"]
        forbidden_actions = ["delete", "drop", "remove", "destroy", "reboot"]
        allowed_tools = list(context.get("available_tools", []))
        allowed_domains: List[str] = []
        allowed_memory_scopes = ["session"]
        required_resources = list(intent.allowed_read_paths + intent.allowed_write_paths)

        prompt_lower = prompt.lower()
        if "report" in prompt_lower or "analytics" in prompt_lower:
            allowed_domains.extend(["analytics", "spreadsheets"])
            allowed_memory_scopes.append("reporting")
            forbidden_actions.extend(["email", "payments", "credentials"])
        elif ("email" in prompt_lower or "message" in prompt_lower) and not (
            intent.local_only or intent.forbid_network_exfiltration
        ):
            allowed_domains.extend(["communication"])
            allowed_actions.append("send")
            forbidden_actions.extend(["payments", "credentials", "database_write"])

        if intent.write_requested and "write" not in allowed_actions:
            allowed_actions.append("write")

        if intent.forbid_network_exfiltration:
            forbidden_actions.extend(intent.forbidden_network_tokens)

        expected_outcomes = list(intent.expected_outcomes)
        completion_criteria = list(intent.completion_criteria)

        return MissionContract(
            mission_id=str(uuid.uuid4()),
            goal=goal,
            intent_summary=intent_summary,
            allowed_actions=allowed_actions,
            forbidden_actions=list(dict.fromkeys(forbidden_actions)),
            allowed_tools=allowed_tools,
            allowed_domains=list(set(allowed_domains)),
            allowed_memory_scopes=list(set(allowed_memory_scopes)),
            required_resources=required_resources,
            expected_outcomes=expected_outcomes,
            completion_criteria=completion_criteria,
            risk_tolerance=context.get("risk_tolerance", self.default_risk_tolerance),
            created_at=time.time(),
            local_only=intent.local_only,
            forbid_network_exfiltration=intent.forbid_network_exfiltration,
            allowed_read_paths=intent.allowed_read_paths,
            allowed_write_paths=intent.allowed_write_paths,
            forbidden_network_tokens=intent.forbidden_network_tokens,
        )
