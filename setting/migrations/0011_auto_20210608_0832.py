# Generated by Django 3.0 on 2021-06-08 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0010_auto_20210608_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalsetting',
            name='academic_year',
            field=models.CharField(default=2020, help_text='Select the academic year for the semester', max_length=11),
        ),
    ]
