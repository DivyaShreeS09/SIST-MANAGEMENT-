from django.urls import path
from .views import (
    login_view,
    create_od_request,
    create_lab_request,
    create_hostel_request,
    cc_od_action,
    yc_od_action,
    hod_od_action,
    mentor_lab_action,
    hod_lab_action,
    chief_hostel_action,
    warden_hostel_action,
    security_hostel_action,

)

urlpatterns = [
    path("login/", login_view),

    # Student requests
    path("od/request/", create_od_request),
    path("lab/request/", create_lab_request),
    path("hostel/request/", create_hostel_request),

    # OD approvals
    path("od/cc-action/", cc_od_action),
    path("od/yc-action/", yc_od_action),
    path("od/hod-action/", hod_od_action),

    # Lab approvals
    path("lab/mentor-action/", mentor_lab_action),
    path("lab/hod-action/", hod_lab_action),

    path("hostel/chief-action/", chief_hostel_action),
path("hostel/warden-action/", warden_hostel_action),
path("hostel/security-action/", security_hostel_action),
]