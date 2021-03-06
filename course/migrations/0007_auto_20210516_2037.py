# Generated by Django 3.0 on 2021-05-16 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programme', '0007_programme_department'),
        ('lecture', '0002_lecturemodel_programme'),
        ('course', '0006_auto_20210515_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursemodel',
            name='code',
            field=models.CharField(default=None, max_length=100, unique=True, verbose_name='code code'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursemodel',
            name='lecture',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='lecture.LectureModel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursemodel',
            name='programme',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='programme.Programme'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='coursemodel',
            unique_together={('lecture', 'programme')},
        ),
        migrations.RemoveField(
            model_name='coursemodel',
            name='short_name',
        ),
    ]
