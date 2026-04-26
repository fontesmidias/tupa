"""Testes de PolicyVersion + PolicyAcceptance (Story 3.4)."""

from __future__ import annotations

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models import User
from apps.policies.exceptions import PolicyAcceptanceAppendOnlyError
from apps.policies.models import PolicyAcceptance, PolicyKind, PolicyVersion


@pytest.fixture
def user(db):
    return User.objects.create_user(email="u@x.com", password="x")


@pytest.fixture
def terms_v1(db):
    return PolicyVersion.objects.create(
        kind=PolicyKind.TERMS,
        version="1.0.0",
        effective_at=timezone.now(),
        full_text_md="# Termos v1",
        summary_of_changes_md="inicial",
    )


@pytest.fixture
def privacy_v1(db):
    return PolicyVersion.objects.create(
        kind=PolicyKind.PRIVACY,
        version="1.0.0",
        effective_at=timezone.now(),
        full_text_md="# Privacidade v1",
        summary_of_changes_md="inicial",
    )


@pytest.mark.django_db
def test_seed_migration_idempotente():
    """Roda a função seed da migration 0002 duas vezes e valida idempotência."""
    import importlib

    mod = importlib.import_module("apps.policies.migrations.0002_seed_v1")
    # Stub mínimo de "apps" com o model real (substitui o apps do state).
    class _AppsStub:
        def get_model(self, app_label, name):
            return PolicyVersion

    mod.seed(_AppsStub(), None)
    mod.seed(_AppsStub(), None)
    assert PolicyVersion.objects.filter(version="1.0.0").count() == 2


@pytest.mark.django_db
def test_policy_version_unique_kind_version(terms_v1):
    with pytest.raises(IntegrityError):
        PolicyVersion.objects.create(
            kind=PolicyKind.TERMS,
            version="1.0.0",
            effective_at=timezone.now(),
            full_text_md="dup",
        )


@pytest.mark.django_db
def test_policy_acceptance_cria(user, terms_v1):
    acc = PolicyAcceptance.objects.create(
        user=user,
        policy_version=terms_v1,
        ip="127.0.0.1",
        user_agent="ua",
        summary_shown_version="1.0.0",
    )
    assert acc.pk is not None
    assert acc.accepted_at is not None


@pytest.mark.django_db
def test_policy_acceptance_bloqueia_save_em_existente(user, terms_v1):
    acc = PolicyAcceptance.objects.create(user=user, policy_version=terms_v1)
    acc.ip = "1.2.3.4"
    with pytest.raises(PolicyAcceptanceAppendOnlyError):
        acc.save()


@pytest.mark.django_db
def test_policy_acceptance_bloqueia_delete_instancia(user, terms_v1):
    acc = PolicyAcceptance.objects.create(user=user, policy_version=terms_v1)
    with pytest.raises(PolicyAcceptanceAppendOnlyError):
        acc.delete()


@pytest.mark.django_db
def test_policy_acceptance_bloqueia_update_massa(user, terms_v1):
    PolicyAcceptance.objects.create(user=user, policy_version=terms_v1)
    with pytest.raises(PolicyAcceptanceAppendOnlyError):
        PolicyAcceptance.objects.filter(user=user).update(ip="9.9.9.9")


@pytest.mark.django_db
def test_policy_acceptance_bloqueia_delete_massa(user, terms_v1):
    PolicyAcceptance.objects.create(user=user, policy_version=terms_v1)
    with pytest.raises(PolicyAcceptanceAppendOnlyError):
        PolicyAcceptance.objects.filter(user=user).delete()
