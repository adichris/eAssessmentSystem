# Generated by Django 3.0 on 2021-06-07 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0044_studenttheoryscript_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studenttheoryscript',
            name='score',
        ),
        migrations.AddField(
            model_name='studenttheoryscript',
            name='total_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
