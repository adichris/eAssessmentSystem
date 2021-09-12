# Generated by Django 3.2.5 on 2021-09-09 13:33

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=accounts.models.upload_user_to_path),
        ),
    ]
