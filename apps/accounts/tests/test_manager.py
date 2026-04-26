"""Testes UserManager (Story 2.1)."""

from __future__ import annotations

import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_create_user_basic():
    u = User.objects.create_user(email="a@b.com", password="pwd")
    assert u.email == "a@b.com"
    assert u.check_password("pwd")
    assert u.is_staff is False
    assert u.is_superuser is False


@pytest.mark.django_db
def test_create_user_no_email_raises():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="x")


@pytest.mark.django_db
def test_create_user_normalizes_email():
    u = User.objects.create_user(email="  Foo@Bar.COM ".strip(), password="x")
    assert u.email == "foo@bar.com"


@pytest.mark.django_db
def test_create_superuser():
    u = User.objects.create_superuser(email="root@x.com", password="pwd")
    assert u.is_staff is True
    assert u.is_superuser is True
    assert u.is_active is True


@pytest.mark.django_db
def test_create_superuser_requires_is_staff():
    with pytest.raises(ValueError):
        User.objects.create_superuser(email="r@x.com", password="p", is_staff=False)


@pytest.mark.django_db
def test_create_superuser_requires_is_superuser():
    with pytest.raises(ValueError):
        User.objects.create_superuser(email="r@x.com", password="p", is_superuser=False)
