# Generated by Django 3.0 on 2021-05-22 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_auto_20210518_1403'),
        ('assessment', '0013_auto_20210518_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('question_number', 'updated')},
        ),
        migrations.AddField(
            model_name='question',
            name='question_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='course',
            field=models.ForeignKey(help_text='The course to hold the questions', on_delete=django.db.models.deletion.CASCADE, to='course.CourseModel'),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='total_marks',
            field=models.IntegerField(default=5),
        ),
    ]
