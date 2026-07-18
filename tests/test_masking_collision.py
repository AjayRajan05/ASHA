"""Collision-safe masking: same entity → same token, different → different."""

from asha import sanitize
from asha.types.results import SanitizeResult


def test_same_email_produces_same_mask_token():
    """The same email appearing twice must produce the same mask token."""
    prompt = "Email a@b.com and again a@b.com"
    result = sanitize(prompt)
    assert isinstance(result, SanitizeResult)
    masked = result.output

    # Both occurrences of a@b.com should be masked
    assert "a@b.com" not in masked

    # Find all mask tokens containing EMAIL or HASH
    tokens = [t for t in masked.split() if "EMAIL" in t or "HASH" in t]
    email_tokens = [t for t in tokens if "EMAIL" in t]

    # Must have at least 2 mask tokens (one for each occurrence)
    assert len(email_tokens) >= 2, (
        f"Expected >= 2 EMAIL tokens in masked output, got {len(email_tokens)}: {masked!r}"
    )
    # Same email → same token
    assert email_tokens[0] == email_tokens[1], (
        f"Same email should produce same token: {email_tokens}"
    )


def test_different_emails_produce_different_mask_tokens():
    """Two different emails must produce different mask tokens."""
    prompt = "Email a@b.com and c@d.com"
    result = sanitize(prompt)
    assert isinstance(result, SanitizeResult)
    masked = result.output

    # Both emails should be masked
    assert "a@b.com" not in masked
    assert "c@d.com" not in masked

    import re
    found = re.findall(r"\[EMAIL[^\]]*\][^\s]*", masked)

    # Must have at least 2 different mask tokens
    assert len(found) >= 2, (
        f"Expected >= 2 EMAIL mask tokens, got {len(found)}: {masked!r}"
    )
    # Different emails → different tokens
    assert found[0] != found[1], (
        f"Different emails should produce different tokens: {found}"
    )
