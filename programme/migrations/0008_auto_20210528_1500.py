# Generated by Django 3.0 on 2021-05-28 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programme', '0007_programme_department'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programme',
            options={'ordering': ('name', 'pk')},
        ),
    ]
