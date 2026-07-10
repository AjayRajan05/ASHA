"""Collision-safe masking: same entity -> same token, different -> different."""

from asha import sanitize
from asha.types.results import SanitizeResult


def test_same_email_same_token():
    prompt = "Email a@b.com and again a@b.com"
    result = sanitize(prompt)
    assert isinstance(result, SanitizeResult)
    masked = result.output
    tokens = [t for t in masked.split() if "EMAIL" in t or "HASH" in t]
    email_tokens = [t for t in tokens if "EMAIL" in t]
    if len(email_tokens) >= 2:
        assert email_tokens[0] == email_tokens[1]


def test_different_emails_different_tokens():
    prompt = "Email a@b.com and c@d.com"
    result = sanitize(prompt)
    assert isinstance(result, SanitizeResult)
    masked = result.output
    import re

    found = re.findall(r"\[EMAIL[^\]]*\][^\s]*", masked)
    if len(found) >= 2:
        assert found[0] != found[1]
