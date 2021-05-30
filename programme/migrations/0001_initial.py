# Generated by Django 3.0 on 2021-05-09 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0005_auto_20210509_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('course', models.ManyToManyField(to='course.CourseModel')),
            ],
        ),
    ]
