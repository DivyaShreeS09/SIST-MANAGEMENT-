from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.db.models import Q
import json
import threading

from datetime import datetime, timedelta

from accounts.models import User, ApproverAssignment
from od.models import ODRequest
from lab.models import LabRequest
from hostel.models import HostelOutpassRequest


def safe_name(user_obj):
    if not user_obj:
        return "—"
    return user_obj.full_name or user_obj.username or "—"


def send_od_approval_email(student, od, cc_name, yc_name, hod_name, final_status):
    """Send a structured OD approval/rejection email to the student."""
    if not student.email:
        return
    status_word = "APPROVED" if final_status == "APPROVED" else "REJECTED"
    subject = f"OD Request {status_word} – SIST Management System"
    body = f"""Hello {student.full_name},

Your OD request has been {status_word}.

Student Details:
  Name        : {student.full_name}
  Register No : {student.register_no}
  Program     : {student.program}
  Section     : {student.section}

OD Details:
  Reason : {od.reason}
  From   : {od.from_date}  {od.from_time}
  To     : {od.to_date}  {od.to_time}

Approvals:
  Class Coordinator : {cc_name}
  Year Coordinator  : {yc_name}
  HOD               : {hod_name}

Final Status : {status_word}

{"Please log in to the SIST Management System to download your OD letter." if final_status == "APPROVED" else "Please contact your Class Coordinator for further assistance."}

Regards,
SIST Management System"""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [student.email], fail_silently=True)
    except Exception as e:
        print("OD email failed:", e)


def send_status_email(student, request_type, status_text, extra_details=None):
    """Generic status email used for Lab and Hostel requests."""
    if not student.email:
        return

    try:
        send_mail(
            f"{request_type} Request {status_text}",
            f"""Hello {student.full_name},

Your {request_type} request has been {status_text}.

{extra_details or ""}

Regards,
SIST Management System""",
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=True,
        )
    except Exception as e:
        print("Email failed:", e)


def get_all_od_requests(request):
    od_qs = ODRequest.objects.select_related(
        "student", "cc_action_by", "yc_action_by", "hod_action_by"
    )

    # Filter by approver's assignments when approver_id is provided.
    # Student dashboard calls without approver_id and gets all records (backward compat).
    approver_id = request.GET.get("approver_id", "").strip()
    if approver_id:
        assignments = ApproverAssignment.objects.filter(approver_id=approver_id)
        if assignments.exists():
            q = Q()
            for a in assignments:
                cond = Q(student__program__iexact=a.program)
                if a.year:
                    cond &= Q(student__year=str(a.year))
                if a.section:
                    cond &= Q(student__section__iexact=a.section)
                q |= cond
            od_qs = od_qs.filter(q)
        else:
            od_qs = od_qs.none()

    # Newest first — student sees latest requests at top; approver dashboards re-sort in JS
    od_list = od_qs.order_by("-created_at")

    data = []
    for od in od_list:
        data.append({
            "id": od.id,
            "studentId": od.student.id,
            "regNo": od.student.register_no,
            "studentName": od.student.full_name,
            "program": od.student.program,
            "section": od.student.section,
            "year": od.student.year,
            "dept": od.student.department,
            "reason": od.reason,
            "fromDate": str(od.from_date),
            "toDate": str(od.to_date),
            "fromTime": str(od.from_time),
            "toTime": str(od.to_time),
            "proof_url": od.proof_file.url if od.proof_file else "",
            "statusCC": od.cc_status,
            "statusYC": od.yc_status,
            "statusHOD": od.hod_status,
            "finalStatus": od.final_status,
            "createdAt": str(od.created_at),
            "ccByName": od.cc_action_by.full_name if od.cc_action_by else "Pending",
            "ycByName": od.yc_action_by.full_name if od.yc_action_by else "Pending",
            "hodByName": od.hod_action_by.full_name if od.hod_action_by else "Pending",
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
def create_od_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST"}, status=405)

    try:
        student = User.objects.get(id=request.POST.get("student_id"))

        from_date = request.POST.get("from_date")
        from_time = request.POST.get("from_time")
        is_emergency = request.POST.get("is_emergency") == "true"

        now = datetime.now()
        od_time = datetime.strptime(f"{from_date} {from_time}", "%Y-%m-%d %H:%M")

        if not is_emergency and (od_time - now < timedelta(hours=12)):
            return JsonResponse({
                "error": "OD must be applied 12 hours before OR mark as Emergency"
            }, status=400)

        od = ODRequest.objects.create(
            student=student,
            reason=request.POST.get("reason"),
            from_date=from_date,
            to_date=request.POST.get("to_date"),
            from_time=from_time,
            to_time=request.POST.get("to_time"),
            proof_file=request.FILES.get("proof_file"),
            is_emergency=is_emergency
        )

        # EMERGENCY EMAIL — only assigned CC/YC/HOD for this student's program+year+section
        if is_emergency:
            approvers_list = list(
                ApproverAssignment.objects.filter(
                    program=student.program,
                    year=student.year,
                    section=student.section,
                    role__in=["CLASS_COORDINATOR", "YEAR_COORDINATOR"]
                ).select_related("approver")
            )

            # Snapshot values needed so the thread needs no DB access
            student_name = student.full_name
            student_reg  = student.register_no
            student_sec  = student.section
            od_reason    = od.reason
            od_to_date   = str(od.to_date)
            od_to_time   = str(od.to_time)

            def _send_emergency():
                for a in approvers_list:
                    if not a.approver.email:
                        continue
                    send_mail(
                        "URGENT OD Request – Action Required",
                        f"""Hello {safe_name(a.approver)},

A new OD request requires your approval.

Student     : {student_name}
Register No : {student_reg}
Section     : {student_sec}
Reason      : {od_reason}
From        : {from_date}  {from_time}
To          : {od_to_date}  {od_to_time}

Please log in to the system to review and take action.

Regards,
SIST Management System""",
                        settings.DEFAULT_FROM_EMAIL,
                        [a.approver.email],
                        fail_silently=True,
                    )

            threading.Thread(target=_send_emergency, daemon=True).start()

        return JsonResponse({
            "status": "success",
            "id": od.id,
            "proof_url": od.proof_file.url if od.proof_file else ""
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def cc_od_action(request):
    try:
        print("CC ACTION - body:", request.body)
        data = json.loads(request.body)

        request_id = data.get("request_id")
        action = data.get("action")
        approver_id = data.get("approver_id")

        if not request_id or not action:
            return JsonResponse({"error": "Missing request_id or action"}, status=400)

        with transaction.atomic():
            od = ODRequest.objects.select_for_update().get(id=request_id)

            if od.final_status == "REJECTED":
                return JsonResponse({"error": "Already rejected"}, status=400)

            if od.cc_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            od.cc_status = action
            od.cc_action_by_id = approver_id

            if action == "REJECTED":
                od.final_status = "REJECTED"

            od.save()

        # After CC approves, notify the assigned HOD (only if not already rejected)
        if action == "APPROVED" and od.final_status != "REJECTED":
            hod_assignment = ApproverAssignment.objects.filter(
                program=od.student.program,
                role="HOD"
            ).filter(
                Q(year__isnull=True) | Q(year=od.student.year)
            ).select_related("approver").first()

            print("HOD assignment:", hod_assignment)  # DEBUG

            if hod_assignment and hod_assignment.approver.email:
                print("Sending email to:", hod_assignment.approver.email)  # DEBUG

                hod_email    = hod_assignment.approver.email
                hod_name     = safe_name(hod_assignment.approver)
                student_name = od.student.full_name
                student_reg  = od.student.register_no
                student_sec  = od.student.section
                od_reason    = od.reason
                od_from      = f"{od.from_date}  {od.from_time}"
                od_to        = f"{od.to_date}  {od.to_time}"

                def _send_hod_cc():
                    send_mail(
                        "URGENT OD Request – HOD Approval Required",
                        f"""Hello {hod_name},

An OD request has been approved by CC and requires your final approval.

Student     : {student_name}
Register No : {student_reg}
Section     : {student_sec}
Reason      : {od_reason}
From        : {od_from}
To          : {od_to}

Please log in and take action.

Regards,
SIST Management System""",
                        settings.DEFAULT_FROM_EMAIL,
                        [hod_email],
                        fail_silently=True,
                    )
                threading.Thread(target=_send_hod_cc, daemon=True).start()

            else:
                print("HOD NOT FOUND or EMAIL MISSING")  # DEBUG

        return JsonResponse({"status": "success"})

    except ODRequest.DoesNotExist:
        return JsonResponse({"error": "OD request not found in database"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        print("CC ACTION ERROR:", str(e))
        return JsonResponse({"error": str(e)}, status=400)



@csrf_exempt
def yc_od_action(request):
    try:
        print("YC ACTION - body:", request.body)
        data = json.loads(request.body)

        request_id = data.get("request_id")
        action = data.get("action")
        approver_id = data.get("approver_id")

        if not request_id or not action:
            return JsonResponse({"error": "Missing request_id or action"}, status=400)

        with transaction.atomic():
            od = ODRequest.objects.select_for_update().get(id=request_id)

            if od.final_status == "REJECTED":
                return JsonResponse({"error": "Already rejected"}, status=400)

            if od.yc_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            od.yc_status = action
            od.yc_action_by_id = approver_id

            if action == "REJECTED":
                od.final_status = "REJECTED"

            od.save()

        # After YC approves, notify the assigned HOD (only if not already rejected)
        if action == "APPROVED" and od.final_status != "REJECTED":
            hod_assignment = ApproverAssignment.objects.filter(
                program=od.student.program,
                role="HOD"
            ).filter(
                Q(year__isnull=True) | Q(year=od.student.year)
            ).select_related("approver").first()

            print("HOD assignment:", hod_assignment)  # DEBUG

            if hod_assignment and hod_assignment.approver.email:
                print("Sending email to:", hod_assignment.approver.email)  # DEBUG

                hod_email    = hod_assignment.approver.email
                hod_name     = safe_name(hod_assignment.approver)
                student_name = od.student.full_name
                student_reg  = od.student.register_no
                student_sec  = od.student.section
                od_reason    = od.reason
                od_from      = f"{od.from_date}  {od.from_time}"
                od_to        = f"{od.to_date}  {od.to_time}"

                def _send_hod_yc():
                    send_mail(
                        "URGENT OD Request – HOD Approval Required",
                        f"""Hello {hod_name},

An OD request has been approved by YC and requires your final approval.

Student     : {student_name}
Register No : {student_reg}
Section     : {student_sec}
Reason      : {od_reason}
From        : {od_from}
To          : {od_to}

Please log in and take action.

Regards,
SIST Management System""",
                        settings.DEFAULT_FROM_EMAIL,
                        [hod_email],
                        fail_silently=True,
                    )
                threading.Thread(target=_send_hod_yc, daemon=True).start()

            else:
                print("HOD NOT FOUND or EMAIL MISSING")  # DEBUG

        return JsonResponse({"status": "success"})

    except ODRequest.DoesNotExist:
        return JsonResponse({"error": "OD request not found in database"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        print("YC ACTION ERROR:", str(e))
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def hod_od_action(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            # Plain select_for_update — no select_related to avoid outer-join error on
            # nullable FKs (cc_action_by, yc_action_by) with PostgreSQL FOR UPDATE
            od = ODRequest.objects.select_for_update().get(id=data["request_id"])

            if od.hod_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            if od.cc_status == "REJECTED" or od.yc_status == "REJECTED":
                return JsonResponse({"error": "Already rejected"}, status=400)

            if not (od.cc_status == "APPROVED" or od.yc_status == "APPROVED"):
                return JsonResponse({"error": "CC/YC approval required"}, status=400)

            od.hod_status = data["action"]
            od.hod_action_by_id = data["approver_id"]
            od.final_status = "APPROVED" if data["action"] == "APPROVED" else "REJECTED"

            od.save()

        # Resolve all names in main thread (safe DB access) before spawning thread
        cc_name      = safe_name(od.cc_action_by)
        yc_name      = safe_name(od.yc_action_by)
        hod_name     = safe_name(User.objects.filter(id=data["approver_id"]).first())
        student      = od.student
        final_status = od.final_status

        threading.Thread(
            target=send_od_approval_email,
            args=(student, od, cc_name, yc_name, hod_name, final_status),
            daemon=True
        ).start()

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "").strip()

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        if user.role != role:
            return JsonResponse({"error": "Role mismatch"}, status=403)

        user_assignments = list(
            ApproverAssignment.objects.filter(approver=user)
            .values("role", "program", "year", "section")
        )

        return JsonResponse({
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "register_no": user.register_no,
                "program": user.program,
                "section": user.section,
                "year": user.year,
                "department": user.department,
                "hosteller": user.hosteller,
                "assignments": user_assignments,
            }
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# ---------------------------------------------------------------------------
# DEBUG
# ---------------------------------------------------------------------------

def reset_corrupted_cc_status(_request):
    yc_users = User.objects.filter(role="YEAR_COORDINATOR").values_list("id", flat=True)

    affected = ODRequest.objects.filter(
        cc_status__in=["APPROVED", "REJECTED"],
        cc_action_by_id__in=yc_users
    )

    count = affected.count()

    affected.update(
        cc_status="PENDING",
        cc_action_by=None
    )

    return JsonResponse({
        "message": "Reset complete",
        "affected": count
    })


# ---------------------------------------------------------------------------
# LAB
# ---------------------------------------------------------------------------

@csrf_exempt
def create_lab_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST"}, status=405)

    try:
        student = User.objects.get(id=request.POST.get("student_id"))

        lab = LabRequest.objects.create(
            student=student,
            lab_name=request.POST.get("lab"),
            reason=request.POST.get("reason"),
            from_date=request.POST.get("from_date"),
            to_date=request.POST.get("to_date"),
            from_time=request.POST.get("from_time"),
            to_time=request.POST.get("to_time"),
            proof_file=request.FILES.get("proof_file"),
        )

        return JsonResponse({
            "status": "success",
            "id": lab.id,
            "proof_url": lab.proof_file.url if lab.proof_file else "",
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def mentor_lab_action(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            lab = LabRequest.objects.select_for_update().get(id=data["request_id"])

            if lab.mentor_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            lab.mentor_status = data["action"]
            lab.mentor_action_by_id = data["approver_id"]

            if data["action"] == "REJECTED":
                lab.final_status = "REJECTED"

            lab.save()

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def hod_lab_action(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            lab = LabRequest.objects.select_for_update().get(id=data["request_id"])

            if lab.hod_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            if lab.mentor_status == "REJECTED":
                return JsonResponse({"error": "Already rejected by mentor"}, status=400)

            if lab.mentor_status != "APPROVED":
                return JsonResponse({"error": "Mentor approval required"}, status=400)

            lab.hod_status = data["action"]
            lab.hod_action_by_id = data["approver_id"]
            lab.final_status = "APPROVED" if data["action"] == "APPROVED" else "REJECTED"

            lab.save()

        threading.Thread(
            target=send_status_email,
            args=(lab.student, "Lab", lab.final_status),
            daemon=True
        ).start()

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# ---------------------------------------------------------------------------
# HOSTEL
# ---------------------------------------------------------------------------

@csrf_exempt
def create_hostel_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST"}, status=405)

    try:
        student = User.objects.get(id=request.POST.get("student_id"))

        hos = HostelOutpassRequest.objects.create(
            student=student,
            purpose=request.POST.get("purpose"),
            from_date=request.POST.get("from_date"),
            to_date=request.POST.get("to_date"),
            from_time=request.POST.get("from_time"),
            to_time=request.POST.get("to_time"),
            proof_file=request.FILES.get("proof_file"),
        )

        return JsonResponse({
            "status": "success",
            "id": hos.id,
            "proof_url": hos.proof_file.url if hos.proof_file else "",
            "proof_name": hos.proof_file.name if hos.proof_file else "",
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def chief_hostel_action(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            hos = HostelOutpassRequest.objects.select_for_update().get(id=data["request_id"])

            if hos.chief_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            hos.chief_status = data["action"]
            hos.chief_action_by_id = data["approver_id"]

            if data["action"] == "APPROVED":
                hos.warden_status = "PENDING"
            else:
                hos.final_status = "REJECTED"

            hos.save()

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def warden_hostel_action(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            hos = HostelOutpassRequest.objects.select_for_update().get(id=data["request_id"])

            if hos.warden_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            if hos.chief_status != "APPROVED":
                return JsonResponse({"error": "Chief approval required"}, status=400)

            hos.warden_status = data["action"]
            hos.warden_action_by_id = data["approver_id"]

            if data["action"] == "APPROVED":
                hos.security_status = "PENDING"
            else:
                hos.final_status = "REJECTED"

            hos.save()

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def security_hostel_action(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            hos = HostelOutpassRequest.objects.select_for_update().get(id=data["request_id"])

            if hos.security_status != "PENDING":
                return JsonResponse({"error": "Already processed"}, status=400)

            if hos.warden_status != "APPROVED":
                return JsonResponse({"error": "Warden approval required"}, status=400)

            hos.security_status = data["action"]
            hos.security_action_by_id = data["approver_id"]
            hos.final_status = "APPROVED" if data["action"] == "APPROVED" else "REJECTED"

            hos.save()

        threading.Thread(
            target=send_status_email,
            args=(hos.student, "Hostel Outpass", hos.final_status),
            daemon=True
        ).start()

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)