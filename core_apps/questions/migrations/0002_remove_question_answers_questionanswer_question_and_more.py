# Generated by Django 5.0.1 on 2024-10-03 07:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="answers",
        ),
        migrations.AddField(
            model_name="questionanswer",
            name="question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="q_answers",
                to="questions.question",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="correct_answer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="correct_questions",
                to="questions.questionanswer",
            ),
        ),
    ]