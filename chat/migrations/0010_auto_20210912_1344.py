# Generated by Django 3.2.5 on 2021-09-12 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_alter_groupmessage_group_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grpmsg',
            name='group',
        ),
        migrations.DeleteModel(
            name='GroupMessage',
        ),
        migrations.DeleteModel(
            name='GrpMsg',
        ),
    ]
