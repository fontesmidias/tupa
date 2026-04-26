"""Testes de CircleScoped* + RequisicaoManager via stub — Story 2.7."""

from __future__ import annotations

import pytest

from apps.accounts.tests.factories import (
    CirculoFactory,
    GestorUserFactory,
    RhAdminUserFactory,
    RhOperatorUserFactory,
)
from apps.accounts.tests.models import RequisicaoStub

pytestmark = pytest.mark.django_db


@pytest.fixture
def fixture_reqs():
    c_x = CirculoFactory()
    c_y = CirculoFactory()
    c_z = CirculoFactory()

    gestor_b = GestorUserFactory(circulo=c_x)
    gestor_c = GestorUserFactory(circulo=c_z)

    r1 = RequisicaoStub.objects.create(circulo=c_x, criado_por=gestor_b, titulo="b-x")
    r2 = RequisicaoStub.objects.create(circulo=c_x, criado_por=gestor_c, titulo="c-x")
    r3 = RequisicaoStub.objects.create(circulo=c_y, criado_por=gestor_b, titulo="b-y")
    r4 = RequisicaoStub.objects.create(circulo=c_z, criado_por=gestor_c, titulo="c-z")

    return {
        "c_x": c_x, "c_y": c_y, "c_z": c_z,
        "gestor_b": gestor_b, "gestor_c": gestor_c,
        "r1": r1, "r2": r2, "r3": r3, "r4": r4,
    }


def test_rh_admin_sees_all(fixture_reqs):
    rh = RhAdminUserFactory()
    qs = RequisicaoStub.objects.for_user(rh)
    assert qs.count() == 4


def test_rh_operator_sees_all(fixture_reqs):
    rh = RhOperatorUserFactory()
    qs = RequisicaoStub.objects.for_user(rh)
    assert qs.count() == 4


def test_gestor_sees_own_circle_plus_own_creations(fixture_reqs):
    # gestor_b no círculo X: vê r1 (b-x), r2 (c-x, mesmo círculo), r3 (b-y, próprio criador).
    # NÃO vê r4 (c-z, círculo alheio e criador alheio).
    gestor_b = fixture_reqs["gestor_b"]
    qs = RequisicaoStub.objects.for_user(gestor_b)
    titles = set(qs.values_list("titulo", flat=True))
    assert titles == {"b-x", "c-x", "b-y"}


def test_gestor_does_not_see_foreign_circle(fixture_reqs):
    gestor_b = fixture_reqs["gestor_b"]
    qs = RequisicaoStub.objects.for_user(gestor_b)
    assert not qs.filter(titulo="c-z").exists()


def test_gestor_without_circle_sees_only_own_creations():
    gestor = GestorUserFactory(circulo=None)
    other = GestorUserFactory()
    mine = RequisicaoStub.objects.create(circulo=None, criado_por=gestor, titulo="m")
    RequisicaoStub.objects.create(circulo=None, criado_por=other, titulo="o")
    qs = RequisicaoStub.objects.for_user(gestor)
    assert list(qs) == [mine]


def test_anonymous_returns_none():
    from django.contrib.auth.models import AnonymousUser

    qs = RequisicaoStub.objects.for_user(AnonymousUser())
    assert qs.count() == 0
