"""Factories para apps.accounts — Story 2.1."""

from __future__ import annotations

from typing import Any

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.accounts.models import Circulo, Tomador

User = get_user_model()


class TomadorFactory(DjangoModelFactory):
    class Meta:
        model = Tomador

    nome = factory.Sequence(lambda n: f"Tomador {n}")
    dominio_email = factory.Sequence(lambda n: f"tomador{n}.local")


class CirculoFactory(DjangoModelFactory):
    class Meta:
        model = Circulo

    nome = factory.Sequence(lambda n: f"Circulo {n}")
    descricao = "stub"


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@test.local")
    nome = "Test User"
    is_active = True

    @classmethod
    def _create(cls, model_class: type, *args: Any, **kwargs: Any) -> Any:
        password = kwargs.pop("password", "test123")
        email = kwargs.pop("email")
        return model_class.objects.create_user(email=email, password=password, **kwargs)


class RhAdminUserFactory(UserFactory):
    is_staff = True
    role = "rh_admin"
    email = factory.Sequence(lambda n: f"rh_admin{n}@test.local")
    nome = "RH Admin"


class RhOperatorUserFactory(UserFactory):
    role = "rh_operator"
    email = factory.Sequence(lambda n: f"rh_operator{n}@test.local")
    nome = "RH Operator"


class GestorUserFactory(UserFactory):
    email = factory.Sequence(lambda n: f"gestor{n}@test.local")
    nome = "Gestor B"
    tipo_gestor = "B"
    role = "gestor"
    tomador = factory.SubFactory(TomadorFactory)
