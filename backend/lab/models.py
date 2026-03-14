from django.conf import settings
from django.db import models


class LabRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_requests'
    )

    lab_name = models.CharField(max_length=150)
    reason = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    proof_file = models.FileField(upload_to='lab_proofs/')

    mentor_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    hod_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    mentor_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_lab_actions'
    )
    hod_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hod_lab_actions'
    )

    final_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lab - {self.student.full_name} - {self.final_status}"