"""Story 3.7 — User.cpf EncryptedCharField (criptografia em repouso via Fernet)."""

from __future__ import annotations

from django.db import migrations

from apps.core.fields import EncryptedCharField


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_user_opt_in_flags"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="cpf",
            field=EncryptedCharField(blank=True, max_length=64, null=True),
        ),
    ]
