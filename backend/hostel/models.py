from django.conf import settings
from django.db import models


class HostelOutpassRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hostel_requests'
    )

    purpose = models.TextField()
    from_date = models.DateField()
    to_date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    proof_file = models.FileField(upload_to='hostel_proofs/')

    chief_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    warden_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LOCKED')
    security_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LOCKED')

    chief_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chief_hostel_actions'
    )
    warden_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warden_hostel_actions'
    )
    security_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_hostel_actions'
    )

    final_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hostel - {self.student.full_name} - {self.final_status}"