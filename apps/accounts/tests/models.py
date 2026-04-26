"""Models só-de-teste do app accounts — Story 2.7.

`RequisicaoStub` exercita `CircleScopedQuerySet.for_user` antes do model
real da Story 5.1 existir. Tabela é criada via syncdb no test DB (ver
`config.settings.test._DisableMigrations`).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.accounts.managers import CircleScopedQuerySet, RequisicaoManager


class RequisicaoStub(models.Model):
    circulo = models.ForeignKey(
        "accounts.Circulo",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )
    titulo = models.CharField(max_length=80, default="stub")

    objects: RequisicaoManager = RequisicaoManager.from_queryset(CircleScopedQuerySet)()  # type: ignore[assignment]

    class Meta:
        app_label = "accounts"
