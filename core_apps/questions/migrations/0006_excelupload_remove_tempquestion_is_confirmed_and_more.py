# Generated by Django 5.0.1 on 2024-12-31 22:40

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_answer_tempquestion_tempanswer'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='excel_uploads/')),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('processed', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='tempquestion',
            name='is_confirmed',
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='hint',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='subjects',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='systems',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='topics',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='video_hint',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='years',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tempquestion',
            name='language',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tempquestion',
            name='level',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tempquestion',
            name='specificity',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tempquestion',
            name='excel_upload',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='temp_questions', to='questions.excelupload'),
            preserve_default=False,
        ),
    ]
