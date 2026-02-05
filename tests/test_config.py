from pdf_translator.config import Config


def test_use_vision_accepts_truthy_env_values(monkeypatch):
    for value in ["1", "true", "TRUE", "yes", "on"]:
        monkeypatch.setenv("PDF_TRANSLATOR_USE_VISION", value)
        assert Config().use_vision is True


def test_use_vision_accepts_falsy_env_values(monkeypatch):
    for value in ["0", "false", "FALSE", "no", "off"]:
        monkeypatch.setenv("PDF_TRANSLATOR_USE_VISION", value)
        assert Config().use_vision is False


def test_use_vision_falls_back_to_default_for_invalid_values(monkeypatch):
    monkeypatch.setenv("PDF_TRANSLATOR_USE_VISION", "sometimes")
    assert Config().use_vision is True
