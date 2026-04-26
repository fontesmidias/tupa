"""Dramatiq @idempotent_actor decorator (ADR-010, ADR-011)."""

from __future__ import annotations

import hashlib
import json
import uuid
from functools import wraps
from typing import Any, Callable

import dramatiq
from django.utils import timezone


def _compute_args_hash(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    payload = json.dumps({"args": list(args), "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _get_message_id() -> str:
    try:
        message = dramatiq.middleware.CurrentMessage.get_current_message()
        if message is not None:
            return str(message.message_id)
    except Exception:
        pass
    return str(uuid.uuid4())


def idempotent_actor(*actor_args: Any, **actor_kwargs: Any) -> Callable[[Callable[..., Any]], Any]:
    """Decorator que wrappa dramatiq.actor com idempotência via JobExecutionLog."""

    def decorator(fn: Callable[..., Any]) -> Any:
        actor_name = actor_kwargs.get("actor_name", fn.__name__)

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from apps.core.models import JobExecutionLog

            args_hash = _compute_args_hash(args, kwargs)
            existing = JobExecutionLog.objects.filter(
                actor_name=actor_name,
                args_hash=args_hash,
                status=JobExecutionLog.Status.SUCCESS,
            ).first()
            if existing is not None:
                JobExecutionLog.objects.create(
                    actor_name=actor_name,
                    message_id=_get_message_id(),
                    args_hash=args_hash,
                    status=JobExecutionLog.Status.SKIPPED_DUPLICATE,
                    started_at=timezone.now(),
                    finished_at=timezone.now(),
                )
                return None

            log = JobExecutionLog.objects.create(
                actor_name=actor_name,
                message_id=_get_message_id(),
                args_hash=args_hash,
                status=JobExecutionLog.Status.PENDING,
                started_at=timezone.now(),
            )
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                log.status = JobExecutionLog.Status.FAILED
                log.error_text = str(exc)
                log.finished_at = timezone.now()
                log.save(update_fields=["status", "error_text", "finished_at"])
                raise
            log.status = JobExecutionLog.Status.SUCCESS
            log.finished_at = timezone.now()
            log.save(update_fields=["status", "finished_at"])
            return result

        kwargs_for_actor = dict(actor_kwargs)
        kwargs_for_actor.setdefault("queue_name", "default")
        return dramatiq.actor(*actor_args, **kwargs_for_actor)(wrapper)

    return decorator
