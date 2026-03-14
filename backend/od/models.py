from django.conf import settings
from django.db import models


class ODRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='od_requests'
    )

    reason = models.TextField()
    from_date = models.DateField()
    to_date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    proof_file = models.FileField(upload_to='od_proofs/')

    cc_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    yc_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    hod_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    cc_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cc_od_actions'
    )
    yc_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yc_od_actions'
    )
    hod_action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hod_od_actions'
    )

    final_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OD - {self.student.full_name} - {self.final_status}"