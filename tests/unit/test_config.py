from pathlib import Path

import pytest

from src.config import ConfigError, load_settings

EXAMPLE = Path("config/.env.example")
FAKE_KEY = "sk-invented-key-123"


def _read_example() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in EXAMPLE.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            values[key] = value
    return values


def _write_env(tmp_path: Path, overrides: dict[str, str | None]) -> Path:
    """Copy the example file, set the key, apply overrides (None removes a key)."""
    values = _read_example()
    values["OPENAI_API_KEY"] = FAKE_KEY
    for key, value in overrides.items():
        if value is None:
            values.pop(key)
        else:
            values[key] = value
    env_file = tmp_path / ".env"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in values.items()), encoding="utf-8")
    return env_file


def test_example_file_loads_with_every_default(tmp_path):
    settings = load_settings(_write_env(tmp_path, {}), {})
    assert settings.llm.model == "gpt-6.1-sol"
    assert settings.llm.max_concurrency == 5
    assert settings.data.cv_folder == Path("data/sample/cvs")
    assert settings.evaluation.top_k == 3
    assert settings.server.port == 8000
    assert settings.logging.file == Path("logs/app.log")


def test_nfr_002_api_key_hidden_from_repr_and_str(tmp_path):
    settings = load_settings(_write_env(tmp_path, {}), {})
    assert settings.llm.api_key == FAKE_KEY
    assert FAKE_KEY not in repr(settings)
    assert FAKE_KEY not in str(settings.llm)


def test_missing_setting_fails_clearly_naming_the_key(tmp_path):
    env_file = _write_env(tmp_path, {"LLM_MODEL": None})
    with pytest.raises(ConfigError, match="LLM_MODEL"):
        load_settings(env_file, {})


def test_empty_api_key_fails_clearly_naming_the_key(tmp_path):
    env_file = _write_env(tmp_path, {"OPENAI_API_KEY": ""})
    with pytest.raises(ConfigError, match="OPENAI_API_KEY"):
        load_settings(env_file, {})


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("LLM_MAX_TOKENS", "many"),
        ("LLM_MAX_CONCURRENCY", "0"),
        ("SERVER_PORT", "70000"),
        ("EVAL_MIN_DATE_MATCH_PERCENT", "101"),
        ("LOG_LEVEL", "LOUD"),
    ],
)
def test_invalid_value_fails_clearly_naming_the_key(tmp_path, key, value):
    env_file = _write_env(tmp_path, {key: value})
    with pytest.raises(ConfigError, match=key):
        load_settings(env_file, {})


def test_environment_variable_overrides_env_file(tmp_path):
    env_file = _write_env(tmp_path, {"SERVER_PORT": "8000"})
    settings = load_settings(env_file, {"SERVER_PORT": "9100"})
    assert settings.server.port == 9100


def test_dec_013_server_host_comes_from_the_setting(tmp_path):
    env_file = _write_env(tmp_path, {"SERVER_HOST": "127.0.0.1"})
    assert load_settings(env_file, {}).server.host == "127.0.0.1"
    assert load_settings(env_file, {"SERVER_HOST": "10.0.0.5"}).server.host == "10.0.0.5"


def test_environment_alone_is_enough_when_the_env_file_is_absent(tmp_path):
    values = _read_example()
    values["OPENAI_API_KEY"] = FAKE_KEY
    settings = load_settings(tmp_path / "absent.env", values)
    assert settings.llm.api_key == FAKE_KEY
