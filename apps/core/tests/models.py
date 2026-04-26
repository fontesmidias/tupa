"""Models concretos só para teste dos mixins abstratos."""

from __future__ import annotations

from django.db import models

from apps.core.base_models import SoftDeleteModel, TimestampedModel, UUIDModel
from apps.core.fields import EncryptedCharField


class ConcreteTimestamped(TimestampedModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "core"


class ConcreteUUID(UUIDModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "core"


class ConcreteSoftDelete(SoftDeleteModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "core"


class ConcreteEncrypted(models.Model):
    secret = EncryptedCharField(null=True, blank=True)

    class Meta:
        app_label = "core"
