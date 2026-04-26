"""Testes do @idempotent_actor (Story 1.5b)."""

from __future__ import annotations

import dramatiq
import pytest
from dramatiq.brokers.stub import StubBroker

from apps.core.models import JobExecutionLog
from apps.core.tasks import _compute_args_hash, idempotent_actor


@pytest.fixture(autouse=True)
def stub_broker() -> StubBroker:
    broker = StubBroker()
    dramatiq.set_broker(broker)
    return broker


@pytest.mark.django_db
def test_idempotent_actor_happy_path() -> None:
    calls: list[int] = []

    @idempotent_actor(actor_name="sum_job")
    def sum_job(a: int, b: int) -> int:
        calls.append(a + b)
        return a + b

    sum_job.fn(2, 3)
    assert calls == [5]
    log = JobExecutionLog.objects.get(actor_name="sum_job")
    assert log.status == JobExecutionLog.Status.SUCCESS
    assert log.finished_at is not None


@pytest.mark.django_db
def test_idempotent_actor_skips_duplicate() -> None:
    calls: list[int] = []

    @idempotent_actor(actor_name="dup_job")
    def dup_job(x: int) -> int:
        calls.append(x)
        return x

    dup_job.fn(7)
    dup_job.fn(7)
    assert calls == [7], "Segunda execução não deve chamar a função"
    logs = JobExecutionLog.objects.filter(actor_name="dup_job").order_by("started_at")
    assert logs.count() == 2
    assert logs[0].status == JobExecutionLog.Status.SUCCESS
    assert logs[1].status == JobExecutionLog.Status.SKIPPED_DUPLICATE


@pytest.mark.django_db
def test_idempotent_actor_records_failure() -> None:
    @idempotent_actor(actor_name="fail_job")
    def fail_job(x: int) -> int:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        fail_job.fn(1)

    log = JobExecutionLog.objects.get(actor_name="fail_job")
    assert log.status == JobExecutionLog.Status.FAILED
    assert log.error_text == "boom"
    assert log.finished_at is not None


def test_compute_args_hash_stable() -> None:
    h1 = _compute_args_hash((1, 2), {"a": 1})
    h2 = _compute_args_hash((1, 2), {"a": 1})
    h3 = _compute_args_hash((1, 3), {"a": 1})
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64
