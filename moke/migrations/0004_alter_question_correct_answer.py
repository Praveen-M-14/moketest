# Generated by Django 5.1.4 on 2024-12-12 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moke', '0003_question_correct_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='correct_answer',
            field=models.TextField(blank=True, null=True),
        ),
    ]
