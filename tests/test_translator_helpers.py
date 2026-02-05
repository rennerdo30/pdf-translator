from types import SimpleNamespace

from pdf_translator.translator import _extract_response_text, translate_text_with_chunking


class DummyTranslator:
    def __init__(self, response_prefix="translated"):
        self.calls = []
        self.response_prefix = response_prefix

    def translate_text(self, text: str) -> str:
        self.calls.append(text)
        return f"{self.response_prefix}:{text}"


def test_extract_response_text_handles_string_content():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="  hello world  "))]
    )
    assert _extract_response_text(response) == "hello world"


def test_extract_response_text_handles_part_list_content():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=[{"text": "hello "}, {"text": "world"}])
            )
        ]
    )
    assert _extract_response_text(response) == "hello world"


def test_extract_response_text_handles_missing_content():
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))])
    assert _extract_response_text(response) == ""


def test_translate_text_with_chunking_splits_and_joins():
    translator = DummyTranslator()
    text = "alpha.\n\nbeta.\n\ngamma."

    result = translate_text_with_chunking(translator, text, max_chars=10)

    assert result == "translated:alpha.\n\ntranslated:beta.\n\ntranslated:gamma."
    assert len(translator.calls) == 3


def test_translate_text_with_chunking_skips_empty_text():
    translator = DummyTranslator()
    assert translate_text_with_chunking(translator, "   ", max_chars=10) == ""
    assert translator.calls == []
