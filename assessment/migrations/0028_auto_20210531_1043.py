# Generated by Django 3.0 on 2021-05-31 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0027_auto_20210531_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentpreference',
            name='start_time',
            field=models.TimeField(blank=True, help_text='Assessment start time', null=True),
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='instruction',
            field=models.CharField(default='answer all questions', help_text='Assessment instruction. eg:ANSWER ALL QUESTIONS,', max_length=150),
        ),
    ]
