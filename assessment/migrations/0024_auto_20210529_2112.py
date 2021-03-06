# Generated by Django 3.0 on 2021-05-29 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_auto_20210528_1500'),
        ('course', '0009_auto_20210518_1403'),
        ('assessment', '0023_auto_20210529_0236'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiChoiceScripts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.CourseModel')),
                ('question_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessment.QuestionGroup')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.Student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentMultiChoiceAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessment.QuestionGroup')),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessment.MultiChoiceScripts')),
                ('selected_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assessment.MultiChoiceQuestion')),
            ],
        ),
        migrations.DeleteModel(
            name='StudentMultiChoiceAnswers',
        ),
    ]
