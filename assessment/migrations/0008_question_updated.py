# Generated by Django 3.0 on 2021-05-17 20:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0007_questiongroup_questions_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
