# Generated by Django 3.0 on 2021-05-26 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0019_auto_20210526_2118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessmentpreference',
            name='is_restricted',
        ),
        migrations.AddField(
            model_name='assessmentpreference',
            name='is_question_shuffle',
            field=models.BooleanField(default=False, help_text='Rearrange questions for each student', verbose_name='Shuffle Questions'),
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='due_date',
            field=models.DateTimeField(blank=True, help_text='The date and time assessment is schedule to', null=True),
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='duration',
            field=models.TimeField(blank=True, help_text='The assessment duration in hours:minutes (eg; 2:30)', null=True),
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='environment',
            field=models.CharField(blank=True, choices=[('class', 'Class Room'), ('any', 'Any Place'), ('Home', 'Home Work')], help_text='select how the assessment should be conducted', max_length=120, null=True),
        ),
    ]
