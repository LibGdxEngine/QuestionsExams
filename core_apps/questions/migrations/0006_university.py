# Generated by Django 5.0.1 on 2024-06-27 19:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0005_report"),
    ]

    operations = [
        migrations.CreateModel(
            name="University",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
        ),
    ]
