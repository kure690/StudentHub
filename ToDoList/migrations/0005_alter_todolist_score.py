# Generated by Django 5.0.2 on 2024-04-04 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDoList', '0004_todolist_perfect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todolist',
            name='score',
            field=models.IntegerField(),
        ),
    ]