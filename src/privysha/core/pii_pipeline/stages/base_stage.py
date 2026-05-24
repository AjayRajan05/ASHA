"""
Base Stage for PII Pipeline - Foundation for all PII detection stages
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import time
import uuid


class StageStatus(Enum):
    """Stage execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PIIEntity:
    """PII entity detected in text"""

    text: str
    start: int
    end: int
    pii_type: str
    confidence: float
    context: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StageResult:
    """Result from a PII pipeline stage"""

    success: bool
    stage_name: str
    execution_time_ms: float
    entities: List[PIIEntity] = None
    processed_text: str = ""
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        if self.entities is None:
            self.entities = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PIIContext:
    """Shared context between PII pipeline stages"""

    session_id: str
    original_text: str
    current_text: str
    entities: List[PIIEntity]
    stage_results: Dict[str, StageResult]
    config: Dict[str, Any]
    debug_enabled: bool = False

    def __post_init__(self) -> None:
        if self.entities is None:
            self.entities = []
        if self.stage_results is None:
            self.stage_results = {}

    def get_stage_result(self, stage_name: str) -> Optional[StageResult]:
        """Get result from a specific stage"""
        return self.stage_results.get(stage_name)

    def add_stage_result(self, result: StageResult) -> None:
        """Add result from a stage"""
        self.stage_results[result.stage_name] = result

    def update_entities(self, entities: List[PIIEntity]) -> None:
        """Update entities list"""
        self.entities = entities

    def update_text(self, text: str) -> None:
        """Update current text"""
        self.current_text = text

    def get_successful_stages(self) -> List[str]:
        """Get list of successful stage names"""
        return [name for name, res in self.stage_results.items() if res.success]

    def get_failed_stages(self) -> List[str]:
        """Get list of failed stage names"""
        return [name for name, res in self.stage_results.items() if not res.success]

    def get_total_execution_time(self) -> float:
        """Get total execution time in ms"""
        return sum(res.execution_time_ms for res in self.stage_results.values())


class BaseStage(ABC):
    """Base class for all PII pipeline stages"""

    def __init__(self, stage_name: str) -> None:
        self.stage_name = stage_name
        self.status = StageStatus.PENDING
        self.execution_time_ms = 0.0

    @abstractmethod
    def execute(self, context: PIIContext) -> StageResult:
        """
        Execute the stage logic

        Args:
            context: PII pipeline context

        Returns:
            StageResult with execution results
        """

    @abstractmethod
    def validate_input(self, context: PIIContext) -> bool:
        """
        Validate input for the stage

        Args:
            context: PII pipeline context

        Returns:
            True if input is valid
        """

    def fallback(self, context: PIIContext) -> StageResult:
        """
        Fallback execution if main execution fails

        Args:
            context: PII pipeline context

        Returns:
            StageResult with fallback results
        """
        return StageResult(
            success=False,
            stage_name=self.stage_name,
            execution_time_ms=0.0,
            error=f"Fallback not implemented for {self.stage_name}",
        )

    def process(self, context: PIIContext) -> StageResult:
        """
        Main processing method with error handling

        Args:
            context: PII pipeline context

        Returns:
            StageResult with execution results
        """
        start_time = time.time()
        self.status = StageStatus.RUNNING

        try:
            # Validate input
            if not self.validate_input(context):
                raise ValueError(f"Invalid input for {self.stage_name}")

            # Execute stage
            result = self.execute(context)

            # Update context
            context.add_stage_result(result)
            if result.entities:
                context.update_entities(result.entities)
            if result.processed_text:
                context.update_text(result.processed_text)

            self.status = StageStatus.COMPLETED
            self.execution_time_ms = (time.time() - start_time) * 1000

            return result

        except Exception as e:
            self.status = StageStatus.FAILED
            self.execution_time_ms = (time.time() - start_time) * 1000

            if context.debug_enabled:
                print(f"[{self.stage_name}] Stage failed: {e}")

            # Try fallback
            try:
                fallback_result = self.fallback(context)
                fallback_result.error = (
                    f"Main failed: {e}. Fallback: {fallback_result.error}"
                )
                return fallback_result
            except Exception as fallback_error:
                return StageResult(
                    success=False,
                    stage_name=self.stage_name,
                    execution_time_ms=self.execution_time_ms,
                    error=f"Main failed: {e}. Fallback failed: {fallback_error}",
                )

    def add_debug_info(
        self, context: PIIContext, message: str, data: Dict[str, Any] = None
    ) -> None:
        """Add debug information to context"""
        if context.debug_enabled:
            debug_msg = f"[{self.stage_name}] {message}"
            if data:
                debug_msg += f" | Data: {data}"
            print(debug_msg)

            # Add to metadata
            if "debug_log" not in context.config:
                context.config["debug_log"] = []
            context.config["debug_log"].append(
                {
                    "stage": self.stage_name,
                    "message": message,
                    "data": data,
                    "timestamp": time.time(),
                }
            )


def create_pii_context(
    text: str, config: Dict[str, Any] = None, debug_enabled: bool = False
) -> PIIContext:
    """
    Create a new PII pipeline context

    Args:
        text: Input text to process
        config: Configuration dictionary
        debug_enabled: Enable debug logging

    Returns:
        PIIContext instance
    """
    if config is None:
        config = {}

    return PIIContext(
        session_id=str(uuid.uuid4()),
        original_text=text,
        current_text=text,
        entities=[],
        stage_results={},
        config=config,
        debug_enabled=debug_enabled,
    )
