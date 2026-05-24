"""Cross-API edge-case matrix tests."""

from privysha import optimize, sanitize, wrap_llm


def test_sanitize_empty_prompt():
    assert sanitize("") == ""


def test_optimize_empty_prompt():
    assert optimize("") == ""


def test_sanitize_unicode_emoji():
    out = sanitize("Contact 📧 user@company.com")
    assert "user@company.com" not in out


def test_optimize_unicode_emoji():
    out = optimize("Summarize 📊 quarterly data", privacy_mode="off")
    assert isinstance(out, str)
    assert len(out) > 0


def test_sanitize_large_prompt_does_not_crash():
    text = "word " * 5000 + " secret@company.com"
    out = sanitize(text)
    assert isinstance(out, str)
    assert "secret@company.com" not in out


def test_optimize_large_prompt_does_not_crash():
    text = "please summarize " + ("data " * 3000)
    out = optimize(text, privacy_mode="off", token_budget=100)
    assert isinstance(out, str)


class _MiniClient:
    def __init__(self):
        self.chat = type(
            "Chat",
            (),
            {
                "completions": type(
                    "C",
                    (),
                    {
                        "create": lambda self, messages, **kw: type(
                            "R",
                            (),
                            {
                                "choices": [
                                    type(
                                        "Ch",
                                        (),
                                        {
                                            "message": type(
                                                "M",
                                                (),
                                                {"content": messages[-1]["content"]},
                                            )()
                                        },
                                    )()
                                ]
                            },
                        )()
                    },
                )()
            },
        )()


def test_wrap_llm_empty_message_content():
    client = _MiniClient()
    wrapped = wrap_llm(client, privacy=False, mode="off")
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": ""}],
    )
    assert response.choices[0].message.content == ""
