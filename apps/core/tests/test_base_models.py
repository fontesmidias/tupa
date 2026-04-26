"""Testes base_models."""

from __future__ import annotations

import uuid

import pytest

from apps.core.tests.models import ConcreteSoftDelete, ConcreteTimestamped, ConcreteUUID


@pytest.mark.django_db
def test_timestamped_sets_created_and_updated() -> None:
    obj = ConcreteTimestamped.objects.create(name="a")
    assert obj.created_at is not None
    assert obj.updated_at is not None
    prev = obj.updated_at
    obj.name = "b"
    obj.save()
    obj.refresh_from_db()
    assert obj.updated_at >= prev


@pytest.mark.django_db
def test_uuid_model_generates_uuid_pk() -> None:
    obj = ConcreteUUID.objects.create(name="x")
    assert isinstance(obj.id, uuid.UUID)


@pytest.mark.django_db
def test_soft_delete_hides_from_default_manager() -> None:
    obj = ConcreteSoftDelete.objects.create(name="x")
    obj.soft_delete()
    assert obj.deleted_at is not None
    assert ConcreteSoftDelete.objects.filter(pk=obj.pk).count() == 0
    assert ConcreteSoftDelete.all_objects.filter(pk=obj.pk).count() == 1


@pytest.mark.django_db
def test_soft_delete_restore() -> None:
    obj = ConcreteSoftDelete.objects.create(name="x")
    obj.soft_delete()
    obj.restore()
    assert obj.deleted_at is None
    assert ConcreteSoftDelete.objects.filter(pk=obj.pk).count() == 1
