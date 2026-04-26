"""Forms do app accounts — Story 2.2 / 2.3 / 2.4."""

from __future__ import annotations

from typing import Any

from django import forms

from apps.accounts.models import Tomador, User
from apps.accounts.services.cadastro import infer_tipo_gestor, match_tomador_by_email


class MagicLinkRequestForm(forms.Form):
    """Form de solicitação de link mágico (email)."""

    email = forms.EmailField(
        max_length=254,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full rounded border border-gray-300 px-3 py-2",
                "autocomplete": "email",
                "placeholder": "seu@email.com",
            }
        ),
    )


class MagicLinkConsumeForm(forms.Form):
    """Form de consumo de código (email + code)."""

    email = forms.EmailField(
        max_length=254,
        widget=forms.HiddenInput(),
    )
    code = forms.RegexField(
        regex=r"^\d{6}$",
        label="Código",
        error_messages={"invalid": "código inválido"},
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded border border-gray-300 px-3 py-2",
                "maxlength": "6",
                "inputmode": "numeric",
                "pattern": "[0-9]{6}",
                "autocomplete": "one-time-code",
            }
        ),
    )


class CompleteProfileForm(forms.ModelForm):  # type: ignore[type-arg]
    """Form de cadastro progressivo — Story 2.4."""

    class Meta:
        model = User
        fields = ["nome", "tipo_gestor", "tomador"]

    def __init__(self, *args: Any, user: User | None = None, **kwargs: Any) -> None:
        if user is not None:
            kwargs.setdefault("instance", user)
            initial = dict(kwargs.get("initial") or {})
            email = user.email
            if not initial.get("tipo_gestor"):
                initial["tipo_gestor"] = user.tipo_gestor or infer_tipo_gestor(email)
            if not initial.get("tomador"):
                tomador = user.tomador or match_tomador_by_email(email)
                initial["tomador"] = tomador.pk if tomador else None
            if not initial.get("nome"):
                initial["nome"] = user.nome
            kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        self.fields["tomador"].queryset = Tomador.objects.all()  # type: ignore[attr-defined]
        self.fields["tomador"].required = True
        self.fields["nome"].required = True
        self.fields["tipo_gestor"].required = True
