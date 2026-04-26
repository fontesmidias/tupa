"""Story 3.6b — isolar escopo de MagicLink (login vs reauth_anonymize)."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_user_cpf_encrypted"),
    ]

    operations = [
        migrations.AddField(
            model_name="magiclink",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("login", "Login"),
                    ("reauth_anonymize", "Reautenticação para anonimizar"),
                ],
                default="login",
                max_length=32,
            ),
        ),
    ]
