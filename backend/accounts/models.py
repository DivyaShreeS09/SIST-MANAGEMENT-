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


class ApproverAssignment(models.Model):
    ROLE_CHOICES = [
        ('CLASS_COORDINATOR', 'Class Coordinator'),
        ('YEAR_COORDINATOR', 'Year Coordinator'),
        ('HOD', 'HOD'),
    ]

    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    program = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    section = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        section_text = self.section if self.section else "ALL"
        return f"{self.approver.full_name} - {self.role} - {self.program} - Year {self.year} - {section_text}"