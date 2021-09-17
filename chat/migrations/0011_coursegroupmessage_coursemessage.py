# Generated by Django 3.2.5 on 2021-09-12 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0011_alter_coursemodel_code'),
        ('chat', '0010_auto_20210912_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseGroupMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='course.coursemodel')),
            ],
        ),
        migrations.CreateModel(
            name='CourseMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('message', models.TextField(blank=True, help_text='Optional', null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.coursegroupmessage')),
            ],
        ),
    ]
