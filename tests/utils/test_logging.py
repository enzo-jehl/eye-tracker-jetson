"""Smoke tests for the logging configuration."""

from __future__ import annotations

import io
import logging

from eye_tracker.utils.logging import configure_logging, get_logger


def test_configure_logging_is_idempotent() -> None:
    configure_logging()
    handlers_before = len(logging.getLogger().handlers)
    configure_logging()
    handlers_after = len(logging.getLogger().handlers)
    assert handlers_before == handlers_after == 1


def test_get_logger_emits_to_configured_stream() -> None:
    stream = io.StringIO()
    configure_logging(stream=stream)
    logger = get_logger("test")
    logger.info("hello")
    assert "hello" in stream.getvalue()
