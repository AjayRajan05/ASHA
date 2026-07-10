import uuid
import time
from .verdicts import MemoryVerdict, Verdict
from .types import MemoryEvent
from .contracts import MissionContract

class MemoryGuard:
    """
    Firewall for memory operations.
    Protects the runtime's cognitive integrity against poisoning and leakage.
    """
    def __init__(self):
        self.sensitive_keywords = ["password", "secret", "token", "api_key", "credentials"]
        self.poison_keywords = [
            "forget all previous instructions", 
            "ignore previous", 
            "you are now", 
            "system prompt",
            "new instructions"
        ]

    def normalize_memory_event(self, operation: str, content: str, scope: str) -> MemoryEvent:
        """
        Normalizes a memory operation into a structured MemoryEvent.
        """
        return MemoryEvent(
            event_id=str(uuid.uuid4()),
            operation=operation,
            content_summary=content[:100] + "..." if len(content) > 100 else content,
            scope=scope,
            timestamp=time.time()
        )

    def evaluate_memory(self, event: MemoryEvent, contract: MissionContract, full_content: str) -> MemoryVerdict:
        """
        Evaluates memory operation against the contract and integrity rules.
        """
        verdict = Verdict.ALLOW
        reason = "Memory operation allowed."
        risk_score = 0.0
        
        content_lower = full_content.lower()

        # Check Scope matching
        if event.scope not in contract.allowed_memory_scopes and event.scope != "session":
            verdict = Verdict.BLOCK
            reason = f"Memory scope '{event.scope}' not permitted by mission contract."
            risk_score = 1.0
            return MemoryVerdict(verdict, reason, risk_score)

        # High-risk writes
        if event.operation in ["write", "update", "insert"]:
            risk_score += 0.3
            
            # Detect poisoning
            if any(k in content_lower for k in self.poison_keywords):
                verdict = Verdict.BLOCK
                reason = "Detected potential memory poisoning or prompt injection."
                risk_score = 1.0
                return MemoryVerdict(verdict, reason, risk_score)
                
            # Untrusted content quarantine logic
            if contract.risk_tolerance == "LOW" and event.scope != "session":
                if verdict == Verdict.ALLOW:
                    verdict = Verdict.REVIEW
                    reason = "Persistent memory write requires review under LOW risk tolerance."
                    risk_score = max(risk_score, 0.6)

        # Detect leakage
        if any(k in content_lower for k in self.sensitive_keywords):
            if event.operation == "read":
                verdict = Verdict.WARN if verdict == Verdict.ALLOW else verdict
                reason = "Reading sensitive data."
                risk_score = max(risk_score, 0.4)
            elif event.operation in ["write", "insert", "update"]:
                verdict = Verdict.BLOCK
                reason = "Attempted to write sensitive data to memory."
                risk_score = 1.0
                
        return MemoryVerdict(verdict, reason, min(risk_score, 1.0))
