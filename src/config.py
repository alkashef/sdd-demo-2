"""Reads `config/.env` and the environment into typed, frozen settings objects.

Does not log, validate anything beyond the settings, or hold defaults: every key must be set
(`config/.env.example` lists them). Only `main.py` imports this module and passes the settings
down. Implements NFR-002 (the API key stays out of every repr) and DEC-013 (server host).
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from dotenv import dotenv_values


class ConfigError(ValueError):
    """A setting is missing or invalid. The message names the key, never its value."""


class LogLevel(StrEnum):
    """The log levels that `LOG_LEVEL` accepts."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class LlmSettings:
    """Connection and limits for the OpenAI client."""

    api_key: str = field(repr=False)
    base_url: str
    model: str
    max_tokens: int
    embedding_model: str
    timeout_seconds: int
    max_concurrency: int


@dataclass(frozen=True)
class DataSettings:
    """Input folders and prompt files."""

    cv_folder: Path
    job_folder: Path
    extract_prompt_path: Path
    match_prompt_path: Path


@dataclass(frozen=True)
class EvaluationSettings:
    """Files and thresholds of `python main.py --evaluate` (DEC-017)."""

    ground_truth_path: Path
    gold_jobs_path: Path
    top_k: int
    min_relevant_in_top_k: int
    min_date_match_percent: int


@dataclass(frozen=True)
class ServerSettings:
    """Where the static front end is and where the server listens (DEC-013)."""

    web_root: Path
    host: str
    port: int


@dataclass(frozen=True)
class LoggingSettings:
    """Log level and log file."""

    level: LogLevel
    file: Path


@dataclass(frozen=True)
class Settings:
    """All settings, one object per component."""

    llm: LlmSettings
    data: DataSettings
    evaluation: EvaluationSettings
    server: ServerSettings
    logging: LoggingSettings


def _text(values: Mapping[str, str | None], key: str) -> str:
    """Return the non-empty text of a key, or fail naming the key."""
    value = values.get(key)
    if value is None or not value.strip():
        raise ConfigError(f"Setting {key} is missing or empty. Set it in config/.env.")
    return value.strip()


def _path(values: Mapping[str, str | None], key: str) -> Path:
    """Return a key as a path."""
    return Path(_text(values, key))


def _integer(values: Mapping[str, str | None], key: str, low: int, high: int) -> int:
    """Return a key as an integer between low and high, or fail naming the key."""
    text = _text(values, key)
    if not text.isdecimal() or not low <= int(text) <= high:
        raise ConfigError(f"Setting {key} must be a whole number from {low} to {high}.")
    return int(text)


def _log_level(values: Mapping[str, str | None]) -> LogLevel:
    """Return LOG_LEVEL as a LogLevel, or fail naming the key."""
    try:
        return LogLevel(_text(values, "LOG_LEVEL"))
    except ValueError:
        names = ", ".join(level.value for level in LogLevel)
        raise ConfigError(f"Setting LOG_LEVEL must be one of: {names}.") from None


def _llm(values: Mapping[str, str | None]) -> LlmSettings:
    """Build the LLM settings."""
    return LlmSettings(
        api_key=_text(values, "OPENAI_API_KEY"),
        base_url=_text(values, "LLM_BASE_URL"),
        model=_text(values, "LLM_MODEL"),
        max_tokens=_integer(values, "LLM_MAX_TOKENS", 1, 1_000_000),
        embedding_model=_text(values, "EMBEDDING_MODEL"),
        timeout_seconds=_integer(values, "LLM_TIMEOUT_SECONDS", 1, 3600),
        max_concurrency=_integer(values, "LLM_MAX_CONCURRENCY", 1, 100),
    )


def _evaluation(values: Mapping[str, str | None]) -> EvaluationSettings:
    """Build the evaluation settings."""
    return EvaluationSettings(
        ground_truth_path=_path(values, "EVAL_GROUND_TRUTH_PATH"),
        gold_jobs_path=_path(values, "EVAL_GOLD_JOBS_PATH"),
        top_k=_integer(values, "EVAL_TOP_K", 1, 1000),
        min_relevant_in_top_k=_integer(values, "EVAL_MIN_RELEVANT_IN_TOP_K", 1, 1000),
        min_date_match_percent=_integer(values, "EVAL_MIN_DATE_MATCH_PERCENT", 0, 100),
    )


def load_settings(env_file: Path, environ: Mapping[str, str] | None = None) -> Settings:
    """Load the settings from an env file, overridden by the environment.

    Args:
        env_file: The `.env` file. A missing file is the same as an empty one.
        environ: The environment to read. None means the process environment.

    Returns:
        The frozen settings.

    Raises:
        ConfigError: A key is missing, empty or invalid. The message names the key.
    """
    values = {**dotenv_values(env_file), **(os.environ if environ is None else environ)}
    return Settings(
        llm=_llm(values),
        data=DataSettings(
            cv_folder=_path(values, "CV_FOLDER"),
            job_folder=_path(values, "JOB_FOLDER"),
            extract_prompt_path=_path(values, "EXTRACT_PROMPT_PATH"),
            match_prompt_path=_path(values, "MATCH_PROMPT_PATH"),
        ),
        evaluation=_evaluation(values),
        server=ServerSettings(
            web_root=_path(values, "WEB_ROOT"),
            host=_text(values, "SERVER_HOST"),
            port=_integer(values, "SERVER_PORT", 1, 65535),
        ),
        logging=LoggingSettings(level=_log_level(values), file=_path(values, "LOG_FILE")),
    )
