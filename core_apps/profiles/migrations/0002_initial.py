# Generated by Django 5.0.1 on 2024-04-21 06:47

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="favoritelist",
            name="questions",
            field=models.ManyToManyField(
                blank=True, related_name="favorite_lists", to="questions.question"
            ),
        ),
    ]