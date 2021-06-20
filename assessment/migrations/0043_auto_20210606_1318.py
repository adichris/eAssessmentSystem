# Generated by Django 3.0 on 2021-06-06 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0042_multichoicescripts_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='studenttheoryscript',
            name='has_paused',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='status',
            field=models.CharField(choices=[('prepared', 'Prepared'), ('marked', 'Marked'), ('conducted', 'Conducted'), ('conduct', 'Conduct'), ('published', 'Published'), ('assessing', 'Assessing')], default='prepared', max_length=25),
        ),
    ]
