# Generated by Django 5.0.2 on 2024-04-25 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDoList', '0011_todolist_assigned_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjects',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subjects',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]