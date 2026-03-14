from django.shortcuts import render
from django.http import Http404

ALLOWED_PAGES = {
    "login.html",
    "student_dashboard.html",
    "student_od.html",
    "student_lab.html",
    "student_hostel.html",
    "admin_od_cc.html",
    "admin_od_yc.html",
    "admin_od_hod.html",
    "admin_lab_cc.html",
    "admin_lab_yc.html",
    "admin_lab_hod.html",
    "admin_hostel_warden.html",
    "admin_hostel_chief.html",
    "admin_hostel_security.html",
    "index.html",
}

def home(request):
    return render(request, "login.html")

def page_view(request, page_name):
    if page_name not in ALLOWED_PAGES:
        raise Http404("Page not found")
    return render(request, page_name)
