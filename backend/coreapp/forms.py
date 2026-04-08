from django import forms
from django.contrib.auth.forms import PasswordResetForm

from accounts.models import User


class UsernamePasswordResetForm(PasswordResetForm):
    """
    Replaces Django's email-based lookup with a username (register number) lookup.
    The field is kept as 'email' internally so Django's PasswordResetForm.save()
    works without modification — it still reads cleaned_data['email'] and sends
    the reset link to user.email.
    """
    email = forms.CharField(
        label="Register Number",
        max_length=150,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Enter your register number',
        })
    )

    def get_users(self, username_input):
        """Return the single active user matching this register number/username."""
        return User.objects.filter(
            username__iexact=username_input.strip(),
            is_active=True,
        ).exclude(email='').exclude(email__isnull=True)
