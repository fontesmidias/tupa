"""Signals do app accounts. Story 2.6 — rotacao de session_key em mudanca de privilegio."""

from __future__ import annotations

from typing import Any

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.accounts.models import User

PRIVILEGE_FIELDS = ("is_staff", "is_superuser", "role")


@receiver(pre_save, sender=User)
def _snapshot_privilege_fields(
    sender: type[User], instance: User, **kwargs: Any
) -> None:
    """Armazena valores anteriores dos campos de privilegio para diff em post_save."""
    if not instance.pk:
        return
    try:
        previous = sender.objects.only(*PRIVILEGE_FIELDS).get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    instance._privilege_snapshot = {  # type: ignore[attr-defined]
        f: getattr(previous, f) for f in PRIVILEGE_FIELDS
    }


@receiver(post_save, sender=User)
def rotate_session_on_privilege_change(
    sender: type[User], instance: User, created: bool, **kwargs: Any
) -> None:
    """Invalida sessoes do user quando campo de privilegio muda (Story 2.6, NFR13)."""
    if created:
        return
    snapshot = getattr(instance, "_privilege_snapshot", None)
    if not snapshot:
        return
    changed = any(snapshot.get(f) != getattr(instance, f) for f in PRIVILEGE_FIELDS)
    if not changed:
        return
    # Invalida todas as sessoes do user (session backend agnostico).
    from django.contrib.sessions.models import Session

    user_id_str = str(instance.pk)
    for session in Session.objects.iterator():
        data = session.get_decoded()
        if data.get("_auth_user_id") == user_id_str:
            session.delete()
