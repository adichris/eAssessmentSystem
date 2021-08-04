# Generated by Django 3.2.5 on 2021-07-23 14:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0003_alter_department_id'),
        ('course', '0010_auto_20210717_0943'),
        ('programme', '0009_alter_programme_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, null=True)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='department.department')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.courselevel')),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programme.programme')),
            ],
        ),
        migrations.AlterField(
            model_name='message',
            name='from_user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL, verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='message',
            name='to_user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_user', to=settings.AUTH_USER_MODEL, verbose_name='To'),
        ),
        migrations.DeleteModel(
            name='AllMessage',
        ),
    ]
