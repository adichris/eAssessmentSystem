# Generated by Django 3.0 on 2021-06-05 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0040_auto_20210604_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='studenttheoryscript',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
