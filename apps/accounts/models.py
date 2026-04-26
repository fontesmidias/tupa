"""Modelos de accounts — User customizado + stubs Tomador/Circulo (Story 2.1)."""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower

from apps.accounts.managers import UserManager
from apps.core.base_models import TimestampedModel, UUIDModel
from apps.core.fields import EncryptedCharField


class Tomador(UUIDModel, TimestampedModel):
    """Stub — expandido em stories futuras."""

    nome = models.CharField(max_length=255)
    dominio_email = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        app_label = "accounts"

    def __str__(self) -> str:
        return self.nome

    @classmethod
    def match_by_email_domain(cls, email: str) -> Tomador | None:
        """Retorna Tomador cujo dominio_email bate com o domínio do email, ou None."""
        if not email or "@" not in email:
            return None
        domain = email.split("@", 1)[1].strip().lower()
        if not domain:
            return None
        return cls.objects.filter(dominio_email__iexact=domain).first()


class Circulo(UUIDModel, TimestampedModel):
    """Stub — expandido em stories futuras."""

    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")

    class Meta:
        app_label = "accounts"

    def __str__(self) -> str:
        return self.nome


class User(AbstractBaseUser, PermissionsMixin):
    """User customizado com PK UUID e autenticação por email."""

    class TipoGestor(models.TextChoices):
        A = "A", "Tipo A"
        B = "B", "Tipo B"
        C = "C", "Tipo C"

    class Role(models.TextChoices):
        RH_ADMIN = "rh_admin", "RH Admin"
        RH_OPERATOR = "rh_operator", "RH Operator"
        GESTOR = "gestor", "Gestor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    nome = models.CharField(max_length=150, blank=True, default="")
    role = models.CharField(
        max_length=16, choices=Role.choices, default=Role.GESTOR
    )
    tipo_gestor = models.CharField(
        max_length=1, choices=TipoGestor.choices, null=True, blank=True
    )
    tomador = models.ForeignKey(
        Tomador,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )
    circulo = models.ForeignKey(
        Circulo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )
    anonimizado_em = models.DateTimeField(null=True, blank=True)

    # Story 3.7 — CPF criptografado em repouso (EncryptedCharField / Fernet).
    cpf = EncryptedCharField(null=True, blank=True, max_length=64)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Story 2.5 — MFA TOTP opt-in para rh_admin.
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = EncryptedCharField(null=True, blank=True, max_length=512)

    # Story 3.6b — flags de opt-in LGPD (default True; revogáveis pelo titular).
    opt_in_marketing = models.BooleanField(default=True)
    opt_in_analytics = models.BooleanField(default=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # noqa: RUF012

    class Meta:
        app_label = "accounts"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="user_email_ci_uniq"),
        ]


    def __str__(self) -> str:
        return self.email

    def save(self, *args: object, **kwargs: object) -> None:
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)  # type: ignore[arg-type]

    @property
    def is_cadastro_completo(self) -> bool:
        return bool(self.nome) and self.tipo_gestor is not None and self.tomador_id is not None

    @property
    def is_rh(self) -> bool:
        """True se role é rh_admin ou rh_operator (Story 2.7)."""
        return self.role in (self.Role.RH_ADMIN, self.Role.RH_OPERATOR)

    @property
    def is_rh_admin(self) -> bool:
        return self.role == self.Role.RH_ADMIN

    @property
    def is_gestor(self) -> bool:
        return self.role == self.Role.GESTOR


class MagicLink(UUIDModel, TimestampedModel):
    """Link mágico (código 6 dígitos) enviado por email — Story 2.2.

    Story 3.6b: `purpose` isola escopos de uso (login vs reauth_anonymize).
    Um link emitido para uma finalidade NUNCA é aceito para outra.
    """

    class Purpose(models.TextChoices):
        LOGIN = "login", "Login"
        REAUTH_ANONYMIZE = "reauth_anonymize", "Reautenticação para anonimizar"

    email = models.EmailField()
    code_hash = models.CharField(max_length=64)
    purpose = models.CharField(
        max_length=32, choices=Purpose.choices, default=Purpose.LOGIN
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "accounts"
        indexes = [
            models.Index(fields=["email", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"MagicLink({self.email})"


class UserDataExport(UUIDModel, TimestampedModel):
    """Registro de export LGPD (Art. 19) — Story 3.6a."""

    class Status(models.TextChoices):
        PENDING = "pending"
        READY = "ready"
        FAILED = "failed"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="data_exports"
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    file_path = models.CharField(max_length=500, blank=True, default="")
    size_bytes = models.BigIntegerField(default=0)
    error_text = models.TextField(blank=True, default="")

    class Meta:
        app_label = "accounts"
        indexes = [
            models.Index(fields=["user", "-created_at"], name="user_export_recent_idx"),
        ]
