# Generated by Django 5.0.2 on 2024-04-04 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDoList', '0002_subjects'),
    ]

    operations = [
        migrations.AddField(
            model_name='todolist',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
