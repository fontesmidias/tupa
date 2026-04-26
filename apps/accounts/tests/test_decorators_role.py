"""Testes dos decorators de role — Story 2.7."""

from __future__ import annotations

import json

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from apps.accounts.decorators import require_role, require_role_any
from apps.accounts.tests.factories import (
    GestorUserFactory,
    RhAdminUserFactory,
    RhOperatorUserFactory,
)

pytestmark = pytest.mark.django_db


def _ok_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


def _mk(user=None, accept: str = "text/html") -> HttpRequest:
    rf = RequestFactory()
    req = rf.get("/x", HTTP_ACCEPT=accept)
    if user is None:
        from django.contrib.auth.models import AnonymousUser

        req.user = AnonymousUser()  # type: ignore[assignment]
    else:
        req.user = user  # type: ignore[assignment]
    return req


def test_require_role_allows_matching_role():
    user = RhAdminUserFactory()
    resp = require_role("rh_admin")(_ok_view)(_mk(user))
    assert resp.status_code == 200
    assert resp.content == b"ok"


def test_require_role_forbids_mismatch_html():
    user = GestorUserFactory()
    resp = require_role("rh_admin")(_ok_view)(_mk(user))
    assert resp.status_code == 403
    assert b"403" in resp.content or b"Forbidden" in resp.content or resp.content


def test_require_role_forbids_mismatch_json():
    user = GestorUserFactory()
    resp = require_role("rh_admin")(_ok_view)(_mk(user, accept="application/json"))
    assert resp.status_code == 403
    payload = json.loads(resp.content)
    assert payload["code"] == "FORBIDDEN"
    assert "message" in payload


def test_require_role_anonymous_401_html():
    resp = require_role("rh_admin")(_ok_view)(_mk(None))
    assert resp.status_code == 401


def test_require_role_anonymous_401_json():
    resp = require_role("rh_admin")(_ok_view)(_mk(None, accept="application/json"))
    assert resp.status_code == 401
    payload = json.loads(resp.content)
    assert payload["code"] == "UNAUTHORIZED"


def test_require_role_any_accepts_first():
    user = RhAdminUserFactory()
    resp = require_role_any("rh_admin", "rh_operator")(_ok_view)(_mk(user))
    assert resp.status_code == 200


def test_require_role_any_accepts_second():
    user = RhOperatorUserFactory()
    resp = require_role_any("rh_admin", "rh_operator")(_ok_view)(_mk(user))
    assert resp.status_code == 200


def test_require_role_any_blocks_gestor():
    user = GestorUserFactory()
    resp = require_role_any("rh_admin", "rh_operator")(_ok_view)(
        _mk(user, accept="application/json")
    )
    assert resp.status_code == 403
    assert json.loads(resp.content)["code"] == "FORBIDDEN"


def test_require_role_any_anonymous_401():
    resp = require_role_any("rh_admin")(_ok_view)(_mk(None))
    assert resp.status_code == 401
