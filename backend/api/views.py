from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json

from accounts.models import User
from od.models import ODRequest
from lab.models import LabRequest
from hostel.models import HostelOutpassRequest


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
        }
    })


@csrf_exempt
def create_od_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        student = User.objects.get(id=data["student_id"])
    except Exception as e:
        return JsonResponse({"error": f"Bad request: {str(e)}"}, status=400)

    od = ODRequest.objects.create(
        student=student,
        reason=data["reason"],
        from_date=data["from_date"],
        to_date=data["to_date"],
        from_time=data["from_time"],
        to_time=data["to_time"],
        proof_file=data.get("proof_file", "")
    )

    return JsonResponse({"status": "success", "id": od.id})


@csrf_exempt
def create_lab_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        student = User.objects.get(id=data["student_id"])

        lab = LabRequest.objects.create(
            student=student,
            lab_name=data["lab"],
            reason=data["reason"],
            from_date=data["from_date"],
            to_date=data["to_date"],
            from_time=data["from_time"],
            to_time=data["to_time"],
            proof_file=data.get("proof_file", "")
        )

        return JsonResponse({"status": "success", "id": lab.id})

    except User.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except KeyError as e:
        return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def create_hostel_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        student = User.objects.get(id=data["student_id"])
    except Exception as e:
        return JsonResponse({"error": f"Bad request: {str(e)}"}, status=400)

    hos = HostelOutpassRequest.objects.create(
        student=student,
        purpose=data["purpose"],
        from_date=data["from_date"],
        to_date=data["to_date"],
        from_time=data["from_time"],
        to_time=data["to_time"],
        proof_file=data.get("proof_file", "")
    )

    return JsonResponse({"status": "success", "id": hos.id})

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

        # reject wins
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

        # reject wins from CC/YC stage
        cc_status = (od.cc_status or "PENDING").upper()
        yc_status = (od.yc_status or "PENDING").upper()

        if cc_status == "REJECTED" or yc_status == "REJECTED":
            return JsonResponse({"error": "Cannot act because CC/YC already rejected"}, status=400)

        if not (cc_status == "APPROVED" or yc_status == "APPROVED"):
            return JsonResponse({"error": "Cannot act before CC/YC approval"}, status=400)

        od.hod_status = action
        od.hod_action_by = approver

        if action == "APPROVED":
            od.final_status = "APPROVED"
        elif action == "REJECTED":
            od.final_status = "REJECTED"

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
        else:
            lab.final_status = "REJECTED"

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
            hos.warden_status = "PENDING"   # unlock next stage

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
            hos.security_status = "PENDING"   # unlock security

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
        else:
            hos.final_status = "REJECTED"

        hos.save()

        return JsonResponse({
            "status": "success",
            "security_status": hos.security_status,
            "final_status": hos.final_status
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)