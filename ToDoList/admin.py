from django.contrib import admin
from .models import ToDoList, Subjects, SubjectSchedule

# Register your models here.

admin.site.register(ToDoList)
admin.site.register(Subjects)
admin.site.register(SubjectSchedule)


