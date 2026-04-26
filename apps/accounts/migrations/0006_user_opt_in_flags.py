"""Story 3.6b — flags de opt-in LGPD (marketing, analytics)."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_userdataexport_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="opt_in_marketing",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="opt_in_analytics",
            field=models.BooleanField(default=True),
        ),
    ]
