# Generated by Django 3.2.5 on 2021-09-10 13:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('department', '0003_alter_department_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='hod',
            field=models.OneToOneField(blank=True, help_text='Change Head of Department status', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hod_user', to=settings.AUTH_USER_MODEL, verbose_name='Head Of Department'),
        ),
    ]
