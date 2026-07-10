"""Cross-API edge-case matrix tests."""

from asha import optimize, sanitize
from asha.integrations import wrap_llm
from asha.types.results import OptimizeResult, SanitizeResult

from conftest import output_of


def test_sanitize_empty_prompt():
    assert output_of(sanitize("")) == ""


def test_optimize_empty_prompt():
    assert output_of(optimize("")) == ""


def test_sanitize_unicode_emoji():
    out = output_of(sanitize("Contact 📧 user@company.com"))
    assert "user@company.com" not in out


def test_optimize_unicode_emoji():
    result = optimize("Summarize 📊 quarterly data")
    assert isinstance(result, OptimizeResult)
    assert len(result.output) > 0


def test_sanitize_large_prompt_does_not_crash():
    text = "word " * 5000 + " secret@company.com"
    result = sanitize(text)
    assert isinstance(result, SanitizeResult)
    assert "secret@company.com" not in result.output


def test_optimize_large_prompt_does_not_crash():
    text = "please summarize " + ("data " * 3000)
    result = optimize(text, token_budget=100)
    assert isinstance(result, OptimizeResult)


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
    wrapped = wrap_llm(client, mode="off")
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": ""}],
    )
    assert response.choices[0].message.content == ""
