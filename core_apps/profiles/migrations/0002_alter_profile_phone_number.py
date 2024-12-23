# Generated by Django 5.0.1 on 2024-10-18 07:34

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                default=None,
                max_length=30,
                null=True,
                region=None,
                verbose_name="phone number",
            ),
        ),
    ]
