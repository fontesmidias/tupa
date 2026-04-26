"""Sanity tests para fixtures globais (Story 1.6)."""

from __future__ import annotations


import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_user_fixture(user):
    assert user is not None
    assert user.pk is not None
    assert "@test.local" in user.email


@pytest.mark.django_db
def test_rh_admin_fixture(rh_admin):
    assert rh_admin.is_staff is True
    assert rh_admin.is_superuser is False


@pytest.mark.django_db
def test_gestor_b_fixture(gestor_b):
    assert gestor_b.tipo_gestor == "B"
    assert gestor_b.tomador_id is not None


@pytest.mark.django_db
def test_authenticated_client(authenticated_client, user):
    assert authenticated_client is not None
    # Sessão autenticada → _auth_user_id presente
    assert "_auth_user_id" in authenticated_client.session
    assert authenticated_client.session["_auth_user_id"] == str(user.pk)


def test_mock_ai_provider(mock_ai_provider):
    assert mock_ai_provider.extract_text("x") == "texto extraído stub"
    assert mock_ai_provider.transcribe("x") == "transcrição stub"
    assert mock_ai_provider.complete("x") == "completion stub"
    assert mock_ai_provider.embed("x") == [0.0] * 8


def test_freeze_time_fixture(freeze_time):
    with freeze_time("2030-01-01 12:00:00"):
        now = timezone.now()
        assert now.year == 2030
        assert now.month == 1


def test_redis_mock(redis_mock):
    redis_mock.set("k", "v")
    assert redis_mock.get("k") == "v"
