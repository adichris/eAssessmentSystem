# Generated by Django 3.0 on 2021-06-01 23:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0032_auto_20210531_1654'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='multichoicescripts',
            options={'verbose_name': 'Multi Choice Script', 'verbose_name_plural': 'Multi Choice Scripts'},
        ),
        migrations.RemoveField(
            model_name='multichoicescripts',
            name='correct_answers',
        ),
    ]