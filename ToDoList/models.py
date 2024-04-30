from django.db import models

# Create your models here.

class Subjects(models.Model):
    Subject_Name = models.CharField(max_length=100)
    Subject_Code = models.CharField(max_length=20)
    users = models.ManyToManyField('authentication.CustomUser')

    def __str__(self):
        return self.Subject_Code
    

class SubjectSchedule(models.Model):
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject.Subject_Code} Schedule ({self.get_day_of_week_display()})"

class ToDoList(models.Model):
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    Subject_Code = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    description = models.TextField(null=True, blank = True)
    status = models.BooleanField(default=False)
    deadline = models.DateField()
    score = models.IntegerField(default=0)
    perfect = models.IntegerField(default=0)
    assigned_user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    

    def __str__(self):
        return self.task
    
    class Meta:
        ordering =['status']



