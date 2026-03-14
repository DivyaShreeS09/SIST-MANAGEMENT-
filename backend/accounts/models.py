from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('CLASS_COORDINATOR', 'Class Coordinator'),
        ('YEAR_COORDINATOR', 'Year Coordinator'),
        ('HOD', 'HOD'),
        ('MENTOR', 'Mentor'),
        ('CHIEF_WARDEN', 'Chief Warden'),
        ('WARDEN', 'Warden'),
        ('SECURITY', 'Security'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=150)

    register_no = models.CharField(max_length=30, blank=True, null=True, unique=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    section = models.CharField(max_length=20, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    hosteller = models.BooleanField(default=False)
    student_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.role}"