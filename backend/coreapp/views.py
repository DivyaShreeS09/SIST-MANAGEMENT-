from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.conf import settings

from coreapp.forms import UsernamePasswordResetForm


class CustomPasswordResetView(PasswordResetView):
    form_class = UsernamePasswordResetForm
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    def form_valid(self, form):
        print("FORM VALID CALLED ✅")
        response = super().form_valid(form)

        user = self.user
        if user.email:
            send_mail(
                "Password Reset Successful – SIST Management",
                f"Hello {user.full_name or user.username},\n\n"
                "Your password has been successfully reset.\n\n"
                "If this wasn't you, please contact the admin immediately.\n\n"
                "Regards,\nSIST Management System",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )

        return response

    def form_invalid(self, form):
        print("FORM INVALID ❌", form.errors)
        return super().form_invalid(form)


def page_view(request, page_name):
    allowed_pages = [
        "login.html",
        "student_dashboard.html",
        "student_od.html",
        "student_lab.html",
        "student_hostel.html",
        "admin_od_cc.html",
        "admin_od_yc.html",
        "admin_od_hod.html",
        "admin_lab_cc.html",
        "admin_lab_hod.html",
        "admin_hostel_chief.html",
        "admin_hostel_warden.html",
        "admin_hostel_security.html",
    ]

    if page_name not in allowed_pages:
        raise Http404("Page not found")

    return render(request, page_name)