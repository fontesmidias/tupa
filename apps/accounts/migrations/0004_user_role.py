"""Story 2.7 — adiciona User.role (rh_admin/rh_operator/gestor)."""

from django.db import migrations, models


def _backfill_roles(apps, schema_editor):  # type: ignore[no-untyped-def]
    User = apps.get_model("accounts", "User")
    # Staff preexistente vira rh_admin; restante permanece default ("gestor").
    User.objects.filter(is_staff=True).update(role="rh_admin")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_mfa"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("rh_admin", "RH Admin"),
                    ("rh_operator", "RH Operator"),
                    ("gestor", "Gestor"),
                ],
                default="gestor",
                max_length=16,
            ),
        ),
        migrations.RunPython(_backfill_roles, migrations.RunPython.noop),
    ]
