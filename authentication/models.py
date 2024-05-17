from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


DEPARTMENT_CHOICES = [
    # College of Engineering
    ('CIVE', 'Civil Engineering'),
    ('MECE', 'Mechanical Engineering'),
    ('ELEC', 'Electrical Engineering'),
    ('ELEN', 'Electronics Engineering'),
    ('COEN', 'Computer Engineering'),
    ('CHEN', 'Chemical Engineering'),

    # College of Computing Studies
    ('COMP', 'Computer Science'),
    ('INFT', 'Information Technology'),
    ('INSY', 'Information Systems'),

    # College of Architecture and Fine Arts
    ('ARCH', 'Architecture'),
    ('INDE', 'Interior Design'),
    ('INDD', 'Industrial Design'),
    ('FNAR', 'Fine Arts'),

    # College of Business and Management
    ('BSAD', 'Business Administration'),
    ('ACCY', 'Accountancy'),
    ('MANA', 'Management'),
    ('MARK', 'Marketing'),
    ('ECON', 'Economics'),

    # College of Education
    ('EEED', 'Elementary Education'),
    ('SEED', 'Secondary Education'),
    ('SPED', 'Special Education'),

    # College of Arts and Sciences
    ('ENGL', 'English'),
    ('MATH', 'Mathematics'),
    ('PSYC', 'Psychology'),
    ('BIOL', 'Biology'),
    ('CHEM', 'Chemistry'),
    ('PHYS', 'Physics'),
    ('COMM', 'Communication'),

    # College of Nursing and Health Sciences
    ('NURS', 'Nursing'),
    ('MEDT', 'Medical Technology'),
    ('PHAR', 'Pharmacy'),
    ('PHYT', 'Physical Therapy'),

    # College of Maritime Education
    ('MARE', 'Marine Engineering'),
    ('MART', 'Marine Transportation'),
]

class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    department = models.CharField(max_length=4, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username