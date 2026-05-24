"""Security fail-closed opt-in tests."""

import privysha.utils.dropin as dropin_mod
from privysha import sanitize
from privysha.utils.dropin_privacy import (
    SECURITY_FAIL_CLOSED_PLACEHOLDER,
    privacy_fallback,
)


def test_privacy_fallback_fail_open_masks_pii():
    out = privacy_fallback("secret@company.com", True, security_fail_closed=False)
    assert "secret@company.com" not in out


def test_privacy_fallback_fail_closed_on_security_error(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("security failed")

    import privysha.utils.dropin_privacy as dp

    monkeypatch.setattr(dp, "run_security_only", boom)
    out = privacy_fallback(
        "secret@company.com", True, security_fail_closed=True
    )
    assert out == SECURITY_FAIL_CLOSED_PLACEHOLDER


def test_sanitize_fail_closed_on_security_error(monkeypatch):
    import privysha.security.service as svc

    def boom(*args, **kwargs):
        raise RuntimeError("security failed")

    monkeypatch.setattr(svc, "run_security_only", boom)
    out = sanitize("secret@company.com", security_fail_closed=True)
    assert out == SECURITY_FAIL_CLOSED_PLACEHOLDER


def test_sanitize_fail_open_on_security_error(monkeypatch):
    import privysha.security.service as svc

    def boom(*args, **kwargs):
        raise RuntimeError("security failed")

    monkeypatch.setattr(svc, "run_security_only", boom)
    out = sanitize("secret@company.com", security_fail_closed=False)
    assert out == "secret@company.com"


def test_process_fail_closed_uses_blocked_fallback(monkeypatch):
    class BrokenPipeline:
        def process(self, **kwargs):
            raise RuntimeError("pipeline failed")

    import privysha.pipeline.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "Pipeline", BrokenPipeline)

    def blocked(prompt, privacy, **kw):
        if kw.get("security_fail_closed"):
            return SECURITY_FAIL_CLOSED_PLACEHOLDER
        return prompt

    monkeypatch.setattr(dropin_mod, "_privacy_fallback", blocked)

    from privysha import process

    result = process(
        "secret@company.com",
        privacy=True,
        security_fail_closed=True,
        return_metrics=True,
    )
    assert result["optimized"] == SECURITY_FAIL_CLOSED_PLACEHOLDER
