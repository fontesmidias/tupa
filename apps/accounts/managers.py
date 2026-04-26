"""UserManager customizado — Story 2.1. + CircleScoped managers — Story 2.7."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager
from django.db import models

if TYPE_CHECKING:
    from apps.accounts.models import User


class UserManager(BaseUserManager["User"]):
    """Manager de User com autenticação por email."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra: Any) -> "User":
        if not email:
            raise ValueError("O campo email é obrigatório.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra: Any) -> "User":
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str, **extra: Any) -> "User":
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        extra.setdefault("role", "rh_admin")
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser precisa is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser precisa is_superuser=True.")
        return self._create_user(email, password, **extra)


class CircleScopedQuerySet(models.QuerySet):  # type: ignore[type-arg]
    """QuerySet com `for_user`: RH vê tudo, gestor vê só do seu círculo + criados por si.

    Para customizar os nomes dos campos, sobrescreva `scope_circulo_field` e
    `scope_criador_field` no Manager que usa este QuerySet.
    """

    scope_circulo_field = "circulo"
    scope_criador_field = "criado_por"

    def for_user(self, user: Any) -> "CircleScopedQuerySet":
        """Filtra registros segundo o papel do usuário (Story 2.7 AC3)."""
        if user is None or getattr(user, "is_anonymous", True):
            return self.none()
        if getattr(user, "is_rh", False):
            return self.all()
        circulo_id = getattr(user, "circulo_id", None)
        q = models.Q(**{f"{self.scope_criador_field}": user})
        if circulo_id is not None:
            q |= models.Q(**{f"{self.scope_circulo_field}_id": circulo_id})
        return self.filter(q)


class CircleScopedManager(models.Manager.from_queryset(CircleScopedQuerySet)):  # type: ignore[misc]
    """Manager base que expõe `for_user` do QuerySet."""

    def for_user(self, user: Any) -> CircleScopedQuerySet:
        qs: CircleScopedQuerySet = self.get_queryset().for_user(user)
        return qs


class RequisicaoManager(CircleScopedManager):
    """Placeholder exportado para Story 5.1. Usado via `Requisicao.objects.for_user(u)`."""
