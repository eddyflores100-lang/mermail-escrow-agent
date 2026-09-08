#!/usr/bin/env python3
"""
SPDX-License-Identifier: AL-1.0
Copyright (c) 2026 AliceLabs LLC. All rights reserved.

circuit_breaker.py — Circuit Breaker + IAM labels for paybox_request_transfer.

Inspired by the mcp-vault-server circuit breaker pattern
(https://github.com/alicelabs-llc/mcp-vault-server).

This integration is OPTIONAL. The MIT core works without it.

Commercial use of this file requires a license from AliceLabs LLC.
Contact: legal@alicelabs.site
"""
from __future__ import annotations

import functools
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """Raised when a call is attempted while the breaker is OPEN."""

    def __init__(self, opened_at: float, cooldown_until: float, failures: int):
        self.opened_at = opened_at
        self.cooldown_until = cooldown_until
        self.failures = failures
        super().__init__(
            f"circuit OPEN since {opened_at:.0f}, "
            f"cooldown until {cooldown_until:.0f}, "
            f"failures={failures}"
        )


@dataclass
class IAMLabels:
    """IAM-style labels attached to every paybox_request_transfer call."""
    deal_id: str
    buyer_id: str           # sha256(buyer_email)[:12]
    seller_id: str          # sha256(seller_email)[:12]
    phase: str              # "funding" | "release" | "refund"
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempt: int = 1
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    @classmethod
    def for_deal(cls, deal_record: dict, phase: str) -> "IAMLabels":
        return cls(
            deal_id=deal_record["deal_id"],
            buyer_id=hashlib.sha256(deal_record["buyer_email"].encode()).hexdigest()[:12],
            seller_id=hashlib.sha256(deal_record["seller_email"].encode()).hexdigest()[:12],
            phase=phase,
        )

    def to_dict(self) -> dict:
        return {
            "deal_id": self.deal_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "phase": self.phase,
            "call_id": self.call_id,
            "attempt": self.attempt,
            "timestamp": self.timestamp,
        }


@dataclass
class CircuitBreaker:
    """Circuit breaker for paybox_request_transfer calls.

    States:
        CLOSED    → all calls go through
        OPEN      → all calls fail fast with CircuitOpenError
        HALF_OPEN → limited probe traffic (1 call) to test recovery

    Trips on:
        - N consecutive failures (failure_threshold)
        - Any call exceeding latency_threshold_ms

    Recovers:
        - After cooldown_seconds, transitions OPEN → HALF_OPEN
        - In HALF_OPEN, one probe call is allowed
        - If the probe succeeds → CLOSED
        - If the probe fails → OPEN (cooldown doubles, capped at max_cooldown_seconds)
    """
    failure_threshold: int = 5
    latency_threshold_ms: int = 10000
    cooldown_seconds: int = 60
    max_cooldown_seconds: int = 600
    half_open_max_calls: int = 1

    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    opened_at: float = 0.0
    cooldown_until: float = 0.0
    current_cooldown: int = 60
    half_open_calls_in_flight: int = 0

    def _now(self) -> float:
        return time.time()

    def _check_state_transition(self) -> None:
        """Maybe transition OPEN → HALF_OPEN if cooldown has elapsed."""
        if self.state == CircuitState.OPEN and self._now() >= self.cooldown_until:
            self.state = CircuitState.HALF_OPEN
            self.half_open_calls_in_flight = 0

    def _trip(self) -> None:
        """Trip the breaker to OPEN."""
        self.state = CircuitState.OPEN
        self.opened_at = self._now()
        self.cooldown_until = self.opened_at + self.current_cooldown

    def _record_success(self) -> None:
        """Record a successful call."""
        if self.state == CircuitState.HALF_OPEN:
            # Probe succeeded — close the circuit
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.current_cooldown = self.cooldown_seconds  # reset backoff
        elif self.state == CircuitState.CLOSED:
            self.failures = 0  # reset on any success in CLOSED

    def _record_failure(self) -> None:
        """Record a failed call."""
        self.failures += 1
        if self.state == CircuitState.HALF_OPEN:
            # Probe failed — re-open with doubled cooldown
            self.current_cooldown = min(self.current_cooldown * 2, self.max_cooldown_seconds)
            self._trip()
        elif self.state == CircuitState.CLOSED and self.failures >= self.failure_threshold:
            self._trip()

    def _can_attempt_half_open(self) -> bool:
        """In HALF_OPEN, only allow `half_open_max_calls` probe calls."""
        return self.half_open_calls_in_flight < self.half_open_max_calls

    def call(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute `fn` through the circuit breaker.

        Raises:
            CircuitOpenError: if the breaker is OPEN (or HALF_OPEN is saturated)
        """
        self._check_state_transition()

        if self.state == CircuitState.OPEN:
            raise CircuitOpenError(
                self.opened_at, self.cooldown_until, self.failures
            )

        if self.state == CircuitState.HALF_OPEN:
            if not self._can_attempt_half_open():
                raise CircuitOpenError(
                    self.opened_at, self.cooldown_until, self.failures
                )
            self.half_open_calls_in_flight += 1

        start = self._now()
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._record_failure()
            raise
        else:
            latency_ms = (self._now() - start) * 1000
            if latency_ms > self.latency_threshold_ms:
                # Latency trip — counts as a failure
                self._record_failure()
                raise TimeoutError(
                    f"call exceeded latency threshold: {latency_ms:.0f}ms > "
                    f"{self.latency_threshold_ms}ms"
                )
            self._record_success()
            return result

    def status(self) -> dict:
        """Return the current breaker status for audit logging."""
        return {
            "state": self.state.value,
            "failures": self.failures,
            "opened_at": self.opened_at,
            "cooldown_until": self.cooldown_until,
            "current_cooldown": self.current_cooldown,
            "failure_threshold": self.failure_threshold,
            "latency_threshold_ms": self.latency_threshold_ms,
        }

    def reset(self) -> None:
        """Manually reset the breaker (requires buyer approval)."""
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.opened_at = 0.0
        self.cooldown_until = 0.0
        self.current_cooldown = self.cooldown_seconds
        self.half_open_calls_in_flight = 0


# Module-level breaker instance (one per deal in practice)
_breakers: dict[str, CircuitBreaker] = {}


def get_breaker(deal_id: str, **config: Any) -> CircuitBreaker:
    """Get or create a breaker for a deal."""
    if deal_id not in _breakers:
        _breakers[deal_id] = CircuitBreaker(**config)
    return _breakers[deal_id]


def with_circuit_breaker(deal_id: str, phase: str) -> Callable:
    """Decorator that wraps a paybox_request_transfer call with the breaker.

    Usage:
        @with_circuit_breaker("kbd-1a2b3c4d", "release")
        def release_transfer(deal_record, amount, ...):
            return paybox_request_transfer(...)

    The decorated function receives an extra `iam_labels` kwarg.
    """
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(deal_record: dict, *args: Any, **kwargs: Any) -> Any:
            breaker = get_breaker(deal_id)
            labels = IAMLabels.for_deal(deal_record, phase)
            labels.attempt = breaker.failures + 1

            def call_with_labels() -> Any:
                return fn(deal_record, *args, iam_labels=labels.to_dict(), **kwargs)

            return breaker.call(call_with_labels)
        return wrapper
    return decorator


def main() -> int:
    """Demo: simulate a PayBox that fails 3 times then succeeds."""
    import random

    print("=== Circuit breaker demo ===\n")

    breaker = CircuitBreaker(failure_threshold=3, cooldown_seconds=2)

    def fake_paybox_call(attempt: int) -> str:
        # Fail for the first 3 attempts, then succeed
        if attempt <= 3:
            raise RuntimeError(f"PayBox 503 (attempt {attempt})")
        return f"PayBox 200 (attempt {attempt})"

    for attempt in range(1, 8):
        print(f"Attempt {attempt}: state={breaker.state.value}", end="")
        try:
            result = breaker.call(fake_paybox_call, attempt)
            print(f" → SUCCESS: {result}")
        except CircuitOpenError as e:
            print(f" → CIRCUIT_OPEN: {e}")
            time.sleep(1)
        except RuntimeError as e:
            print(f" → FAILED: {e}")
        except TimeoutError as e:
            print(f" → TIMEOUT: {e}")

        # Show breaker status
        status = breaker.status()
        print(f"   breaker: {status['state']}, failures={status['failures']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
