from django.shortcuts import render
from django.http import Http404


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