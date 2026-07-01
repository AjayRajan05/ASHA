import time
import uuid
from .verdicts import ApprovalVerdict, Verdict
from .types import ApprovalRecord

class ApprovalEngine:
    """
    Human approval engine.
    Handles escalation to humans when guards return REVIEW.
    Records decisions and ensures no silent auto-approvals.
    """
    def __init__(self):
        # Hooks for external UI/Slack integrations could be initialized here
        pass

    def request_approval(self, target_id: str, reason: str, context: str = "") -> ApprovalRecord:
        """
        Escalates an action or event for human review.
        This function represents a blocking call until a decision is made.
        """
        # In a fully integrated environment, this would await human input.
        # To satisfy the "no silent auto-approve" rule without hanging headless tests,
        # we default to BLOCK unless explicitly mocked/wired to a real human input.
        
        # simulated_decision = input(f"Review required: {reason} - Approve? (y/N): ")
        simulated_decision = "n"  # default secure
        
        if simulated_decision.lower() == 'y':
            verdict_type = Verdict.ALLOW
            reviewer_reason = "Human explicitly approved."
        else:
            verdict_type = Verdict.BLOCK
            reviewer_reason = "Human rejected or timeout occurred."

        verdict = ApprovalVerdict(
            verdict=verdict_type,
            reason=reviewer_reason,
            reviewer="human_operator"
        )
        
        return ApprovalRecord(
            record_id=str(uuid.uuid4()),
            target_id=target_id,
            verdict=verdict,
            timestamp=time.time()
        )

    def process_verdict(self, verdict_enum: Verdict, reason: str, target_id: str) -> ApprovalRecord:
        """
        Processes standard verdicts or triggers a human review if the verdict is REVIEW.
        """
        if verdict_enum == Verdict.REVIEW:
            return self.request_approval(target_id, reason)
            
        if verdict_enum == Verdict.WARN:
            reason = f"[ACTIONABLE WARNING] {reason}"
            
        verdict = ApprovalVerdict(
            verdict=verdict_enum,
            reason=reason,
            reviewer="system_auto"
        )
        
        return ApprovalRecord(
            record_id=str(uuid.uuid4()),
            target_id=target_id,
            verdict=verdict,
            timestamp=time.time()
        )
