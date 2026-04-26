"""Cobertura do field `role` e properties — Story 2.7."""

from __future__ import annotations

import pytest
from django.contrib.sessions.models import Session
from django.test import Client

from apps.accounts.models import User
from apps.accounts.tests.factories import (
    GestorUserFactory,
    RhAdminUserFactory,
    RhOperatorUserFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def test_default_role_is_gestor():
    u = UserFactory()
    assert u.role == User.Role.GESTOR
    assert u.is_gestor is True
    assert u.is_rh is False


def test_rh_admin_flags():
    u = RhAdminUserFactory()
    assert u.is_rh is True
    assert u.is_rh_admin is True
    assert u.is_gestor is False


def test_rh_operator_flags():
    u = RhOperatorUserFactory()
    assert u.is_rh is True
    assert u.is_rh_admin is False
    assert u.is_gestor is False


def test_create_superuser_sets_role():
    u = User.objects.create_superuser(email="sup@x.com", password="p")
    assert u.role == "rh_admin"
    assert u.is_rh is True


def test_role_change_invalidates_session():
    user = GestorUserFactory(password="p")
    client = Client()
    client.force_login(user)
    assert Session.objects.count() == 1
    user.role = "rh_admin"
    user.save()
    assert Session.objects.count() == 0
