# Generated by Django 3.2.5 on 2021-09-13 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0011_coursegroupmessage_coursemessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursemessage',
            name='title',
        ),
        migrations.AlterField(
            model_name='coursemessage',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
