"""Tests for prompt content preservation.

Gap 2: Safe prompts should be unchanged under mode="off".
Gap 3: Semantic meaning should be preserved.
Gap 4: Instructions/constraints must survive under mode="off".
Gap 5: JSON and code blocks must pass through under mode="off".
"""

import json

from asha.core.policy_config import PolicyConfig
from asha.types.results import ProcessResult, SanitizeResult
from asha.utils.dropin import process, sanitize

from conftest import output_of


# ---------------------------------------------------------------------------
# Gap 2: Safe prompts verbatim preservation under mode="off"
# ---------------------------------------------------------------------------


def test_safe_prompt_verbatim_passthrough_mode_off():
    """A prompt with no PII and no threats must come back verbatim in mode='off'."""
    original = "What is the capital of France?"
    result = process(original, mode="off")
    assert isinstance(result, ProcessResult)
    assert result.output == original


def test_safe_prompt_no_pii_mode_off():
    original = "Summarize the quarterly financial report for stakeholders."
    result = process(original, mode="off")
    assert isinstance(result, ProcessResult)
    assert result.output == original


def test_keyword_survival_mode_lite():
    """mode='lite' produces non-empty output derived from the original."""
    original = "Generate a Python function that sorts a list in ascending order."
    result = process(original, mode="lite")
    assert isinstance(result, ProcessResult)
    assert len(result.output) > 0


# ---------------------------------------------------------------------------
# Gap 3: Semantic meaning / key intent words preserved
# ---------------------------------------------------------------------------


def test_intent_word_customer_support_mode_off():
    """Intent words survive byte-identical in mode='off'."""
    prompt = "I need customer support for my billing issue."
    result = process(prompt, mode="off")
    assert result.output == prompt


def test_intent_words_survive_sanitize():
    """sanitize() should only strip PII/threats, not the intent of the prompt."""
    prompt = "Please help me with my subscription cancellation."
    result = sanitize(prompt)
    assert isinstance(result, SanitizeResult)
    assert "subscription" in result.output
    assert "cancellation" in result.output


def test_domain_keyword_preserved_mode_off():
    """Domain-specific keywords must not be stripped in mode='off'."""
    prompt = "Analyze the neural network architecture for image classification."
    result = process(prompt, mode="off")
    assert result.output == prompt


# ---------------------------------------------------------------------------
# Gap 4: Instructions / constraints preserved under mode="off"
# ---------------------------------------------------------------------------


def test_system_instruction_preserved_mode_off():
    """Instruction text must not be rewritten in mode='off'."""
    instruction = (
        "You MUST respond only in JSON. "
        "Do NOT include any explanation. "
        "Maximum 3 sentences."
    )
    result = process(instruction, mode="off")
    assert result.output == instruction


def test_constraint_preserved_mode_off():
    constraint = "Only use formal language. Never use contractions."
    result = process(constraint, mode="off")
    assert result.output == constraint


def test_numbered_steps_preserved_mode_off():
    prompt = "Step 1: Read the document. Step 2: Summarize it. Step 3: Output JSON."
    result = process(prompt, mode="off")
    assert result.output == prompt


# ---------------------------------------------------------------------------
# Gap 5: JSON / code blocks preserved under mode="off"
# ---------------------------------------------------------------------------


def test_json_payload_preserved_mode_off():
    """A JSON-structured prompt must be byte-identical in mode='off'."""
    payload = {"task": "summarize", "text": "Quarterly revenue increased 12%."}
    prompt = json.dumps(payload)
    result = process(prompt, mode="off")
    assert result.output == prompt


def test_json_prompt_parseable_mode_off():
    """Output from mode='off' on a JSON input should still be valid JSON."""
    payload = json.dumps({"role": "system", "content": "Be concise."})
    result = process(payload, mode="off")
    parsed = json.loads(result.output)
    assert parsed == json.loads(payload)


def test_code_block_preserved_mode_off():
    """Code-like prompts must be byte-identical in mode='off'."""
    code_prompt = (
        "Write a Python function:\n"
        "def calculate_total(items):\n"
        "    return sum(item.price for item in items)"
    )
    result = process(code_prompt, mode="off")
    assert result.output == code_prompt


def test_markdown_code_fence_preserved_mode_off():
    prompt = "```python\nprint('hello world')\n```\nExplain the above code."
    result = process(prompt, mode="off")
    assert result.output == prompt


# ---------------------------------------------------------------------------
# Gap 3: preserve_intent=True - clean prompts returned verbatim
# ---------------------------------------------------------------------------


def test_preserve_intent_returns_original_for_clean_prompt():
    """preserve_intent=True must return the original when no PII / threats found."""
    original = "I need customer support for my billing issue."
    result = process(original, policy=PolicyConfig(preserve_intent=True))
    assert result.output == original


def test_preserve_intent_returns_original_simple():
    """A generic safe prompt is not rewritten when preserve_intent=True."""
    original = "Explain the difference between supervised and unsupervised learning."
    result = process(original, policy=PolicyConfig(preserve_intent=True))
    assert result.output == original


def test_preserve_intent_false_may_rewrite():
    """When preserve_intent=False (default), the optimizer may rewrite clean prompts."""
    original = "Tell me about customer support best practices."
    result = process(original, policy=PolicyConfig(preserve_intent=False))
    assert isinstance(result, ProcessResult)
    assert len(result.output) > 0


def test_preserve_intent_pii_still_masked():
    """Even with preserve_intent=True, PII must be masked when present."""
    prompt = "Contact john.doe@example.com for customer support details."
    result = process(prompt, policy=PolicyConfig(preserve_intent=True))
    assert isinstance(result, ProcessResult)
    assert "john.doe@example.com" not in result.output


# ---------------------------------------------------------------------------
# Gap 4+5: PII in JSON is masked, structure survives
# ---------------------------------------------------------------------------


def test_json_with_pii_masks_email_keeps_structure():
    """When JSON contains PII, the email is masked but the key/value structure stays."""
    payload = json.dumps({"user_email": "alice@corp.com", "action": "delete"})
    result = sanitize(payload)
    assert isinstance(result, SanitizeResult)
    out = output_of(result)
    assert "alice@corp.com" not in out
    assert "delete" in out or "action" in out
