from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

# Create your models here.

User = get_user_model()

class Subjects(models.Model):
    Subject_Name = models.CharField(max_length=100)
    Subject_Code = models.CharField(max_length=20)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, limit_choices_to={'is_teacher': True}, related_name='taught_subjects', null=True, blank=True)
    students = models.ManyToManyField(User, limit_choices_to={'is_student': True}, related_name='enrolled_subjects')

    def __str__(self):
        return self.Subject_Code

    def save(self, *args, **kwargs):
        if not self.teacher:
            self.teacher = User.objects.filter(is_superuser=True).first()
        super().save(*args, **kwargs)

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

    TASK_TYPE_CHOICES = (
        ('activity', 'Activity'),
        ('quiz', 'Quiz'),
    )

    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    Subject_Code = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    description = models.TextField(null=True, blank = True)
    status = models.BooleanField(default=False)
    deadline = models.DateField()
    score = models.IntegerField(default=0)
    perfect = models.IntegerField(default=0)
    assigned_user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES, default='activity')


    def __str__(self):
        return self.task
    
    class Meta:
        ordering =['status']



