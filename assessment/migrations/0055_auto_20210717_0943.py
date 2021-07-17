# Generated by Django 3.2.5 on 2021-07-17 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0054_auto_20210611_2131'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('question_number', 'id', 'updated')},
        ),
        migrations.AlterModelOptions(
            name='studenttheoryanswer',
            options={'ordering': ('question', 'id')},
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Due Date and Time - Deadline'),
        ),
        migrations.AlterField(
            model_name='assessmentpreference',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='multichoicequestion',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='multichoicescripts',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='solution',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='studentmultichoiceanswer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='studenttheoryanswer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='studenttheoryscript',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='theorymarkingscheme',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
