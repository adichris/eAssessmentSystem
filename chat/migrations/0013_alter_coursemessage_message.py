# Generated by Django 3.2.5 on 2021-09-13 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0012_auto_20210913_0203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursemessage',
            name='message',
            field=models.TextField(default='HI'),
            preserve_default=False,
        ),
    ]