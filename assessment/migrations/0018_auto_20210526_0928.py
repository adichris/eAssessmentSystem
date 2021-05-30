# Generated by Django 3.0 on 2021-05-26 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0017_questiongroup_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multichoicequestion',
            name='question',
            field=models.ForeignKey(help_text='Multi-choice question option', on_delete=django.db.models.deletion.CASCADE, to='assessment.Question'),
        ),
    ]
