# Generated by Django 3.0 on 2021-05-17 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_auto_20210516_2053'),
        ('assessment', '0004_auto_20210517_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiongroup',
            name='title',
            field=models.CharField(choices=[('quiz', 'Quiz'), ('quiz1', 'Quiz 1'), ('quiz2', 'Quiz 2'), ('quiz3', 'Quiz 3'), ('quiz4', 'Quiz 4'), ('midsem', 'Mid Semester')], max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='questiongroup',
            unique_together={('title', 'course')},
        ),
    ]
