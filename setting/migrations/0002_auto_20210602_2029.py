# Generated by Django 3.0 on 2021-06-02 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdminSettings',
            new_name='AdminSetting',
        ),
    ]
