from django.db import models

# Create your models here.

class Subjects(models.Model):
    Subject_Name = models.CharField(max_length=100)
    Subject_Code = models.CharField(max_length=20)
    users = models.ManyToManyField('authentication.CustomUser')

    def __str__(self):
        return self.Subject_Code
class ToDoList(models.Model):
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    Subject_Code = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    description = models.TextField(null=True, blank = True)
    status = models.BooleanField(default=False)
    deadline = models.DateField()
    score = models.IntegerField(default=0)
    perfect = models.IntegerField(default=0)
    users = models.ManyToManyField('authentication.CustomUser', related_name='tasks')

    def __str__(self):
        return self.task
    
    class Meta:
        ordering =['status']


