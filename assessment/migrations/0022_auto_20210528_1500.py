# Generated by Django 3.0 on 2021-05-28 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0021_auto_20210528_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentpreference',
            name='instruction',
            field=models.CharField(default='answer all questions', help_text='Quiz or midsem instruction. eg:ANSWER ALL QUESTIONS,', max_length=150),
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='environment',
            field=models.CharField(blank=True, choices=[('class', 'Class Room'), ('any', 'Any Place'), ('home', 'Home Work')], help_text='select how the assessment should be conducted', max_length=120, null=True),
        ),
    ]
