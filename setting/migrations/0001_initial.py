# Generated by Django 3.0 on 2021-06-02 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(choices=[('s1', 'First Semester'), ('s2', 'Second Semester')], max_length=60)),
                ('name_order', models.CharField(choices=[('f', 'First Name'), ('l', 'Last Name')], max_length=20)),
            ],
        ),
    ]