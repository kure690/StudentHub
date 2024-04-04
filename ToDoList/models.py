from django.db import models

# Create your models here.

class ToDoList(models.Model):
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100)
    task = models.CharField(max_length=200)
    description = models.TextField(null=True, blank = True)
    status = models.BooleanField(default=False)
    deadline = models.DateField()

    def __str__(self):
        return self.task
    
    class Meta:
        ordering =['status']

class Subjects(models.Model):
    Subject_Name = models.CharField(max_length=100)
    Subject_Code = models.CharField(max_length=100)
    User

