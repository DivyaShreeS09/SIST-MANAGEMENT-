from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
import json

from accounts.models import User
from od.models import ODRequest
from lab.models import LabRequest
from hostel.models import HostelOutpassRequest


def send_status_email(student, request_type, status_text):
    if not student.email:
        return

    subject = f"{request_type} Request {status_text} - SIST Management System"

    message = f"""
Hello {student.full_name},

Your {request_type} request has been {status_text.lower()}.

Please log in to the SIST Management System to view the latest status and download your approval letter if applicable.

Regards,
SIST Management System
""".strip()

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=False,
    )


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "").strip()
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    if role and user.role != role:
        return JsonResponse({"error": "Role mismatch"}, status=403)

    return JsonResponse({
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.full_name,
            "role": user.role,
            "program": user.program,
            "section": user.section,
            "year": user.year,
            "dept": user.department,
            "hosteller": user.hosteller,
            "email": user.email,
        }
    })


@csrf_exempt
def create_od_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        student_id = request.POST.get("student_id")
        reason = request.POST.get("reason")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        from_time = request.POST.get("from_time")
        to_time = request.POST.get("to_time")
        proof_file = request.FILES.get("proof_file")

        student = User.objects.get(id=student_id)

        od = ODRequest.objects.create(
            student=student,
            reason=reason,
            from_date=from_date,
            to_date=to_date,
            from_time=from_time,
            to_time=to_time,
            proof_file=proof_file,
        )

        return JsonResponse({
            "status": "success",
            "id": od.id,
            "proof_url": od.proof_file.url if od.proof_file else "",
            "proof_name": od.proof_file.name.split("/")[-1] if od.proof_file else "",
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def create_lab_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        student_id = request.POST.get("student_id")
        lab_name = request.POST.get("lab")
        reason = request.POST.get("reason")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        from_time = request.POST.get("from_time")
        to_time = request.POST.get("to_time")
        proof_file = request.FILES.get("proof_file")

        student = User.objects.get(id=student_id)

        lab = LabRequest.objects.create(
            student=student,
            lab_name=lab_name,
            reason=reason,
            from_date=from_date,
            to_date=to_date,
            from_time=from_time,
            to_time=to_time,
            proof_file=proof_file,
        )

        return JsonResponse({
            "status": "success",
            "id": lab.id,
            "proof_url": lab.proof_file.url if lab.proof_file else "",
            "proof_name": lab.proof_file.name.split("/")[-1] if lab.proof_file else "",
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def create_hostel_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        student_id = request.POST.get("student_id")
        purpose = request.POST.get("purpose")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        from_time = request.POST.get("from_time")
        to_time = request.POST.get("to_time")
        proof_file = request.FILES.get("proof_file")

        student = User.objects.get(id=student_id)

        hos = HostelOutpassRequest.objects.create(
            student=student,
            purpose=purpose,
            from_date=from_date,
            to_date=to_date,
            from_time=from_time,
            to_time=to_time,
            proof_file=proof_file,
        )

        return JsonResponse({
            "status": "success",
            "id": hos.id,
            "proof_url": hos.proof_file.url if hos.proof_file else "",
            "proof_name": hos.proof_file.name.split("/")[-1] if hos.proof_file else "",
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def cc_od_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
        action = data.get("action", "").upper()
        approver_id = data.get("approver_id")

        if action not in ["APPROVED", "REJECTED"]:
            return JsonResponse({"error": "Invalid action"}, status=400)

        od = ODRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        od.status_cc = action
        od.cc_by = approver
        od.save()

        return JsonResponse({
            "status": "success",
            "request_id": od.id,
            "cc_status": od.status_cc
        })

    except ODRequest.DoesNotExist:
        return JsonResponse({"error": "OD request not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Approver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def yc_od_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
        action = data.get("action", "").upper()
        approver_id = data.get("approver_id")

        if action not in ["APPROVED", "REJECTED"]:
            return JsonResponse({"error": "Invalid action"}, status=400)

        od = ODRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        od.yc_status = action
        od.yc_action_by = approver

        if action == "REJECTED":
            od.final_status = "REJECTED"

        od.save()

        return JsonResponse({
            "status": "success",
            "request_id": od.id,
            "yc_status": od.yc_status,
            "final_status": od.final_status
        })

    except ODRequest.DoesNotExist:
        return JsonResponse({"error": "OD request not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Approver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def hod_od_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
        action = data.get("action", "").upper()
        approver_id = data.get("approver_id")

        if action not in ["APPROVED", "REJECTED"]:
            return JsonResponse({"error": "Invalid action"}, status=400)

        od = ODRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        cc_status = (od.status_cc or "PENDING").upper()
        yc_status = (od.yc_status or "PENDING").upper()

        if cc_status == "REJECTED" or yc_status == "REJECTED":
            return JsonResponse({"error": "Cannot act because CC/YC already rejected"}, status=400)

        if not (cc_status == "APPROVED" or yc_status == "APPROVED"):
            return JsonResponse({"error": "Cannot act before CC/YC approval"}, status=400)

        od.hod_status = action
        od.hod_action_by = approver

        if action == "APPROVED":
            od.final_status = "APPROVED"
            send_status_email(od.student, "OD", "APPROVED")
        else:
            od.final_status = "REJECTED"
            send_status_email(od.student, "OD", "REJECTED")

        od.save()

        return JsonResponse({
            "status": "success",
            "request_id": od.id,
            "hod_status": od.hod_status,
            "final_status": od.final_status
        })

    except ODRequest.DoesNotExist:
        return JsonResponse({"error": "OD request not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Approver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def mentor_lab_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
        action = data.get("action", "").upper()
        approver_id = data.get("approver_id")

        if action not in ["APPROVED", "REJECTED"]:
            return JsonResponse({"error": "Invalid action"}, status=400)

        lab = LabRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        lab.mentor_status = action
        lab.mentor_action_by = approver

        if action == "REJECTED":
            lab.final_status = "REJECTED"

        lab.save()

        return JsonResponse({
            "status": "success",
            "request_id": lab.id,
            "mentor_status": lab.mentor_status,
            "final_status": lab.final_status
        })

    except LabRequest.DoesNotExist:
        return JsonResponse({"error": "Lab request not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Approver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def hod_lab_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
        action = data.get("action", "").upper()
        approver_id = data.get("approver_id")

        if action not in ["APPROVED", "REJECTED"]:
            return JsonResponse({"error": "Invalid action"}, status=400)

        lab = LabRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        mentor_status = (lab.mentor_status or "PENDING").upper()

        if mentor_status == "REJECTED":
            return JsonResponse({"error": "Cannot act because mentor already rejected"}, status=400)

        if mentor_status != "APPROVED":
            return JsonResponse({"error": "Cannot act before mentor approval"}, status=400)

        lab.hod_status = action
        lab.hod_action_by = approver

        if action == "APPROVED":
            lab.final_status = "APPROVED"
            send_status_email(lab.student, "Lab Access", "APPROVED")
        else:
            lab.final_status = "REJECTED"
            send_status_email(lab.student, "Lab Access", "REJECTED")

        lab.save()

        return JsonResponse({
            "status": "success",
            "request_id": lab.id,
            "hod_status": lab.hod_status,
            "final_status": lab.final_status
        })

    except LabRequest.DoesNotExist:
        return JsonResponse({"error": "Lab request not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Approver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def chief_hostel_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        request_id = data.get("request_id")
        action = data.get("action").upper()
        approver_id = data.get("approver_id")

        hos = HostelOutpassRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        hos.chief_status = action
        hos.chief_action_by = approver

        if action == "APPROVED":
            hos.warden_status = "PENDING"

        if action == "REJECTED":
            hos.final_status = "REJECTED"

        hos.save()

        return JsonResponse({
            "status": "success",
            "chief_status": hos.chief_status
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def warden_hostel_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        request_id = data.get("request_id")
        action = data.get("action").upper()
        approver_id = data.get("approver_id")

        hos = HostelOutpassRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        if hos.chief_status != "APPROVED":
            return JsonResponse({"error": "Chief Warden approval required"}, status=400)

        hos.warden_status = action
        hos.warden_action_by = approver

        if action == "APPROVED":
            hos.security_status = "PENDING"

        if action == "REJECTED":
            hos.final_status = "REJECTED"

        hos.save()

        return JsonResponse({
            "status": "success",
            "warden_status": hos.warden_status
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def security_hostel_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        request_id = data.get("request_id")
        action = data.get("action").upper()
        approver_id = data.get("approver_id")

        hos = HostelOutpassRequest.objects.get(id=request_id)
        approver = User.objects.get(id=approver_id)

        if hos.warden_status != "APPROVED":
            return JsonResponse({"error": "Warden approval required"}, status=400)

        hos.security_status = action
        hos.security_action_by = approver

        if action == "APPROVED":
            hos.final_status = "APPROVED"
            send_status_email(hos.student, "Hostel Outpass", "APPROVED")
        else:
            hos.final_status = "REJECTED"
            send_status_email(hos.student, "Hostel Outpass", "REJECTED")

        hos.save()

        return JsonResponse({
            "status": "success",
            "security_status": hos.security_status,
            "final_status": hos.final_status
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)