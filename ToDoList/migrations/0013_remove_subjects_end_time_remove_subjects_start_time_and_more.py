# Generated by Django 5.0.2 on 2024-04-25 13:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDoList', '0012_subjects_end_time_subjects_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subjects',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='subjects',
            name='start_time',
        ),
        migrations.CreateModel(
            name='SubjectSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ToDoList.subjects')),
            ],
        ),
    ]