from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

import base64
import json
from django.core.files.base import ContentFile

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from .models import Patient, Wound, Assessment, WoundImage, PatientAccess, Profile
from .forms import PatientForm, WoundForm, WoundImageForm


# 🏠 Home
def home(request):
    return HttpResponse("WoundPro_Ke is running 🚀")


# 🏥 Dashboard
@login_required(login_url="/login/")
def dashboard(request):
    user_patients = Patient.objects.filter(user=request.user)

    total_patients = user_patients.count()

    total_wounds = Wound.objects.filter(
        patient__user=request.user
    ).count()

    total_assessments = Assessment.objects.filter(
        wound__patient__user=request.user
    ).count()

    recent_patients = user_patients.order_by('-created_at')[:5]

    return render(request, 'dashboard.html', {
        'total_patients': total_patients,
        'total_wounds': total_wounds,
        'total_assessments': total_assessments,
        'recent_patients': recent_patients,
    })

# 👤 Patient List
@login_required
def patient_list(request):
    patients = Patient.objects.filter(
    Q(user=request.user) |
    Q(access_list__user=request.user)
).distinct()
    return render(request, 'patients/patient_list.html', {'patients': patients})


# ➕ Add Patient
@login_required
def add_patient(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        surname = request.POST.get('surname')
        gender = request.POST.get('gender')
        dob = request.POST.get('date_of_birth')

        if not all([first_name, surname, gender, dob]):
            messages.error(request, "All fields are required.")
            return render(request, 'patients/add_patient.html')

        reg_number = request.POST.get('reg_number', '').strip().upper() or None

        Patient.objects.create(
            user=request.user,   # 🔥 THIS IS THE KEY FIX
            first_name=first_name,
            surname=surname,
            gender=gender,
            date_of_birth=dob,
            reg_number=reg_number,
            general_factors=request.POST.get('general_factors', ''),
            metabolic_factors=request.POST.get('metabolic_factors', ''),
            pathologies=request.POST.get('pathologies', ''),
            surgical_history=request.POST.get('surgical_history', ''),
            allergies=request.POST.get('allergies', ''),
            medication=request.POST.get('medication', ''),
            compliance=request.POST.get('compliance', ''),
            additional_info=request.POST.get('additional_info', ''),
        )

        messages.success(request, "Patient added successfully ✅")
        return redirect('patient_list')

    return render(request, 'patients/add_patient.html')

# 👤 Patient Detail
@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # 🔐 Access control (owner OR shared)
    if not (
        patient.user == request.user or
        PatientAccess.objects.filter(patient=patient, user=request.user).exists()
    ):
        return HttpResponse("Unauthorized", status=403)

    wounds = Wound.objects.filter(patient=patient)

    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'wounds': wounds
    })

# 🩺 Add Wound (AUTO NUMBER + PRECISE LOCATION)
def add_wound(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # JSON POST from the mobile flow
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)

                # Auto wound number
                last_wound = Wound.objects.filter(patient=patient).order_by('-wound_number').first()
                next_number = last_wound.wound_number + 1 if last_wound else 1

                wound = Wound.objects.create(
                    patient=patient,
                    wound_number=next_number,
                    location=data.get('location') or f"Wound #{next_number}",
                    wound_type=data.get('type', ''),
                )

                Assessment.objects.create(
                    wound=wound,
                    wound_type=data.get('type'),
                    aetiology=data.get('aetiology'),
                    duration=data.get('duration'),
                    margins=data.get('margins'),
                    surrounding_skin=data.get('skin'),
                    exudate=data.get('exudate'),
                    progression=data.get('progression'),
                    notes=data.get('assessment_notes'),
                    tissue_epithelial=data.get('tissue', {}).get('epi', 0),
                    tissue_granulation=data.get('tissue', {}).get('gran', 0),
                    tissue_slough=data.get('tissue', {}).get('slough', 0),
                    tissue_necrosis=data.get('tissue', {}).get('necro', 0),
                )

                return JsonResponse({"status": "success", "wound_id": wound.id})

            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)

        # Regular form POST (old flow)
        else:
            location = request.POST.get('location', '').strip()
            if not location:
                messages.error(request, "Please select a body location.")
                return render(request, 'patients/add_wound.html', {'patient': patient})

            precise = request.POST.get('location_precise', '').strip()
            full_location = f"{location} - {precise}" if precise else location

            last_wound = Wound.objects.filter(patient=patient).order_by('-wound_number').first()
            next_number = last_wound.wound_number + 1 if last_wound else 1

            Wound.objects.create(
                patient=patient,
                location=full_location,
                wound_number=next_number
            )

            messages.success(request, "Wound added successfully ✅")
            return redirect('patient_detail', patient_id=patient.id)

    return render(request, 'patients/add_wound.html', {'patient': patient})


# 🔍 Wound Detail
@login_required
def wound_detail(request, wound_id=None):
    if wound_id:
        wound = get_object_or_404(Wound, id=wound_id, patient__user=request.user)
    else:
        wound = Wound.objects.filter(patient__user=request.user).order_by('-id').first()

    if not wound:
        return render(request, 'patients/wound_detail.html', {
            'wound': None,
            'assessments': [],
            'images': []
        })

    assessments = Assessment.objects.filter(wound=wound)
    images = WoundImage.objects.filter(wound=wound)

    return render(request, 'patients/wound_detail.html', {
        'wound': wound,
        'assessments': assessments,
        'images': images
    })


# 📊 Add Assessment (JSON + form fallback)
def add_assessment(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            assessment = Assessment.objects.create(
                wound=wound,
                wound_type=data.get('type'),
                aetiology=data.get('aetiology'),
                duration=data.get('duration'),
                margins=data.get('margins'),
                surrounding_skin=data.get('skin'),
                exudate=data.get('exudate'),
                progression=data.get('progression'),
                notes=data.get('assessment_notes'),
                tissue_epithelial=data.get('tissue', {}).get('epi', 0),
                tissue_granulation=data.get('tissue', {}).get('gran', 0),
                tissue_slough=data.get('tissue', {}).get('slough', 0),
                tissue_necrosis=data.get('tissue', {}).get('necro', 0),
            )

            return JsonResponse({
                "status": "success",
                "id": assessment.id
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    # ✅ FIX: pass wound to template so wound.id and wound.patient.id are available
    return render(request, 'patients/add_assessment.html', {'wound': wound})


# 📷 Upload Image
def upload_image(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)

    if request.method == 'POST':
        form = WoundImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.wound = wound
            img.save()
            return redirect('wound_detail', wound_id=wound.id)
        else:
            print(form.errors)
    else:
        form = WoundImageForm()

    return render(request, 'patients/upload_image.html', {'form': form})


# 📸 Camera Capture
def camera_capture(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)

    if request.method == "POST":
        data = request.POST.get('image_data')

        if not data:
            return HttpResponse("No image data received")

        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]

        file = ContentFile(base64.b64decode(imgstr), name='capture.' + ext)

        WoundImage.objects.create(
            wound=wound,
            image=file
        )

        return redirect('wound_detail', wound_id=wound.id)

    return render(request, 'patients/camera.html')


# 📏 Measure
def measure_wound(request, image_id):
    image = get_object_or_404(WoundImage, id=image_id)
    return render(request, 'patients/measure.html', {'image': image})


# 🌊 Splash
def splash(request):
    return render(request, 'splash.html')


# 🔐 Login View
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import Profile

def login_view(request):
    if request.method == "POST":
        role_selected = request.POST.get("role")
        reg_no = request.POST.get("reg_no")
        password = request.POST.get("password")

        try:
            profile = Profile.objects.get(registration_number=reg_no)
            user = profile.user

            if check_password(password, user.password):
                if profile.role == role_selected:
                    login(request, user)
                    return redirect("/")
                else:
                    messages.error(request, f"This account is not registered as a {role_selected.capitalize()}.")
            else:
                messages.error(request, "Invalid Registration Number or Password.")

        except Profile.DoesNotExist:
            messages.error(request, "Invalid Registration Number or Password.")

    return render(request, "login.html")


# 🚪 Logout
def logout_view(request):
    logout(request)
    return render(request, "logout.html")


# 👤 Profile
@login_required
def profile(request):
    return render(request, 'profile.html')



@login_required
def share_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # 🔐 Only owner can share
    if patient.user != request.user:
        return HttpResponse("Only owner can share this patient", status=403)

    if request.method == "POST":
        reg_no = request.POST.get("registration_number", "").strip().upper()

        if not reg_no:
            messages.error(request, "Registration number is required.")
            return redirect('patient_detail', patient_id=patient.id)

        try:
            profile = Profile.objects.get(registration_number=reg_no)
            target_user = profile.user
        except Profile.DoesNotExist:
            messages.error(request, "User with this registration number not found.")
            return redirect('patient_detail', patient_id=patient.id)

        # 🚫 prevent sharing to self
        if target_user == request.user:
            messages.warning(request, "You already own this patient.")
            return redirect('patient_detail', patient_id=patient.id)

        # 🔁 create or update access
        PatientAccess.objects.get_or_create(
            patient=patient,
            user=target_user,
            defaults={
                "granted_by": request.user,
                "can_edit": False
            }
        )

        messages.success(request, f"Patient shared with {reg_no} successfully ✅")
        return redirect('patient_detail', patient_id=patient.id)

    return HttpResponse("Invalid request", status=400)


@login_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # 🔐 Only owner can delete
    if patient.user != request.user:
        return HttpResponse("Only the owner can delete this patient", status=403)

    if request.method == "POST":
        patient.delete()
        messages.success(request, "Patient deleted successfully 🗑️")
        return redirect('patient_list')

    return render(request, 'patients/confirm_delete.html', {'patient': patient})




from django.http import FileResponse
from reportlab.pdfgen import canvas
import io


@login_required
def wound_pdf(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)

    # 🔐 ACCESS CONTROL
    if not (
        wound.patient.user == request.user or
        PatientAccess.objects.filter(patient=wound.patient, user=request.user).exists()
    ):
        return HttpResponse("Unauthorized", status=403)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # ================= PDF CONTENT =================
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 800, "Wound Report")

    p.setFont("Helvetica", 12)
    p.drawString(50, 770, f"Patient: {wound.patient.first_name} {wound.patient.surname}")
    p.drawString(50, 750, f"Wound #: {wound.wound_number}")
    p.drawString(50, 730, f"Location: {wound.location}")

    p.drawString(50, 700, f"Total Assessments: {wound.assessment_set.count()}")
    p.drawString(50, 680, f"Images: {wound.woundimage_set.count()}")

    y = 650
    for a in wound.assessment_set.all()[:5]:
        p.drawString(50, y, f"- {a.date_assessed.strftime('%Y-%m-%d')} | {a.wound_type or 'N/A'}")
        y -= 20

    p.showPage()
    p.save()

    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f"wound_{wound.id}.pdf")