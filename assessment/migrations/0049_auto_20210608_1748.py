# Generated by Django 3.0 on 2021-06-08 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0048_auto_20210608_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiongroup',
            name='academic_year',
            field=models.CharField(default='2020 / 2021', max_length=20),
        ),
    ]