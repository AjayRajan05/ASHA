import time
import uuid
from typing import Dict, Any, List
from .contracts import MissionContract

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

        # Default conservative scoping
        goal = prompt.strip()
        intent_summary = f"User explicitly requested: {goal}"
        
        # Start with least privilege
        allowed_actions = ["read", "list"]
        forbidden_actions = ["delete", "drop", "remove", "destroy", "format", "reboot"]
        allowed_tools = context.get("available_tools", [])
        allowed_domains = []
        allowed_memory_scopes = ["session"]

        required_resources = []
        expected_outcomes = []
        completion_criteria = ["Goal explicitly satisfied"]

        # Basic deterministic keyword extraction for domains
        prompt_lower = prompt.lower()
        if "report" in prompt_lower or "analytics" in prompt_lower:
            allowed_domains.extend(["analytics", "spreadsheets"])
            allowed_memory_scopes.append("reporting")
            forbidden_actions.extend(["email", "payments", "credentials"])
            expected_outcomes.append("A generated report")
        elif "email" in prompt_lower or "message" in prompt_lower:
            allowed_domains.extend(["communication"])
            allowed_actions.append("send")
            forbidden_actions.extend(["payments", "credentials", "database_write"])
            expected_outcomes.append("A sent message")
            
        if "do not send" in prompt_lower or "externally" in prompt_lower:
            forbidden_actions.extend(["network_request", "Send Network Request", "upload", "send"])

        # The compiler creates the runtime representation
        return MissionContract(
            mission_id=str(uuid.uuid4()),
            goal=goal,
            intent_summary=intent_summary,
            allowed_actions=allowed_actions,
            forbidden_actions=forbidden_actions,
            allowed_tools=allowed_tools,
            allowed_domains=list(set(allowed_domains)),
            allowed_memory_scopes=list(set(allowed_memory_scopes)),
            required_resources=required_resources,
            expected_outcomes=expected_outcomes,
            completion_criteria=completion_criteria,
            risk_tolerance=context.get("risk_tolerance", self.default_risk_tolerance),
            created_at=time.time()
        )
