"""Classification and safe reporting for investigation failures."""

from __future__ import annotations

import socket
from dataclasses import dataclass

import httpx
from langchain_google_genai.chat_models import (
    GoogleAuthenticationError,
    GoogleInvalidRequestError,
    GoogleModelNotFoundError,
    GooglePermissionDeniedError,
)
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError


@dataclass(frozen=True)
class FailureClassification:
    category: str
    message: str
    retryable: bool


_SAFE_FAILURES = {
    "PROVIDER_RATE_LIMITED": (
        "The AI provider is temporarily rate limited.", True
    ),
    "PROVIDER_UNAVAILABLE": (
        "The AI provider is temporarily unavailable.", True
    ),
    "PROVIDER_TIMEOUT": (
        "The AI provider request timed out.", True
    ),
    "PROVIDER_CONNECTION": (
        "A temporary AI provider connection failure occurred.", True
    ),
    "INVALID_CREDENTIALS": (
        "AI provider credentials are invalid or lack permission.", False
    ),
    "INVALID_CONFIGURATION": (
        "The configured AI model or request is invalid.", False
    ),
    "INVALID_REQUEST": (
        "The investigation request is invalid or unsupported.", False
    ),
    "UNSUPPORTED_OPERATION": (
        "The requested AI provider operation is unsupported.", False
    ),
    "UNEXPECTED_ERROR": (
        "An unexpected error occurred during investigation.", False
    ),
}


def _status_code(error: BaseException) -> int | None:
    for candidate in (
        getattr(error, "status_code", None),
        getattr(error, "code", None),
        getattr(error, "status", None),
        getattr(getattr(error, "response", None), "status_code", None),
    ):
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, str) and candidate.isdigit():
            return int(candidate)
        # Google API status enums commonly expose their numeric value here.
        value = getattr(candidate, "value", None)
        if isinstance(value, int):
            return value
    return None


def _error_chain(error: BaseException):
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = (
            current.__cause__
            or current.__context__
            or getattr(current, "orig", None)
        )


def classify_investigation_failure(
    error: BaseException,
) -> FailureClassification:
    chain = tuple(_error_chain(error))

    if any(isinstance(item, (GoogleAuthenticationError, GooglePermissionDeniedError)) for item in chain):
        category = "INVALID_CREDENTIALS"
    elif any(isinstance(item, GoogleModelNotFoundError) for item in chain):
        category = "INVALID_CONFIGURATION"
    elif any(isinstance(item, GoogleInvalidRequestError) for item in chain):
        category = "INVALID_REQUEST"
    elif any(isinstance(item, NotImplementedError) for item in chain):
        category = "UNSUPPORTED_OPERATION"
    else:
        statuses = [_status_code(item) for item in chain]
        statuses = [status for status in statuses if status is not None]
        if any(status in {401, 403} for status in statuses):
            category = "INVALID_CREDENTIALS"
        elif any(status in {405, 501} for status in statuses):
            category = "UNSUPPORTED_OPERATION"
        elif any(status == 429 for status in statuses):
            category = "PROVIDER_RATE_LIMITED"
        elif any(status in {500, 502, 503, 504, 408} for status in statuses):
            category = "PROVIDER_UNAVAILABLE" if any(
                status in {500, 502, 503, 504} for status in statuses
            ) else "PROVIDER_TIMEOUT"
        elif statuses:
            # A structured non-transient HTTP response is not retried.
            category = "INVALID_REQUEST"
        elif any(
            isinstance(item, (httpx.TimeoutException, TimeoutError, RedisTimeoutError))
            for item in chain
        ):
            category = "PROVIDER_TIMEOUT"
        elif any(
            isinstance(
                item,
                (
                    httpx.TransportError,
                    ConnectionError,
                    RedisConnectionError,
                    socket.gaierror,
                ),
            )
            for item in chain
        ):
            category = "PROVIDER_CONNECTION"
        elif any(isinstance(item, ValueError) for item in chain):
            category = "INVALID_REQUEST"
        else:
            # Unknown exceptions, including programming errors, are terminal.
            category = "UNEXPECTED_ERROR"

    message, retryable = _SAFE_FAILURES[category]
    return FailureClassification(category, message, retryable)
