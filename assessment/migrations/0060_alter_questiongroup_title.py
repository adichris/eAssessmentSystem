# Generated by Django 3.2.5 on 2021-09-08 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0059_auto_20210903_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiongroup',
            name='title',
            field=models.CharField(help_text='Assessment title example: Assignment 1 or Quiz 2', max_length=20),
        ),
    ]
