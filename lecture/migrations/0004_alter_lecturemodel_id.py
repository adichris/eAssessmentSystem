# Generated by Django 3.2.5 on 2021-07-17 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lecture', '0003_auto_20210516_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecturemodel',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
