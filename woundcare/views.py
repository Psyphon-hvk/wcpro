from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Patient, Wound, Assessment, WoundImage
from .forms import PatientForm, WoundForm, AssessmentForm, WoundImageForm


# 🏠 Home (optional)
def home(request):
    return HttpResponse("WoundPro_Ke is running 🚀")

from django.contrib.auth.decorators import login_required

# 🏥 Dashboard (MAIN PAGE)
@login_required(login_url="/login/")
def dashboard(request):
    total_patients = Patient.objects.count()
    total_wounds = Wound.objects.count()
    total_assessments = Assessment.objects.count()

    recent_patients = Patient.objects.all().order_by('-id')[:5]

    return render(request, 'dashboard.html', {
        'total_patients': total_patients,
        'total_wounds': total_wounds,
        'total_assessments': total_assessments,
        'recent_patients': recent_patients
    })


# 👤 Patient List
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})


# ➕ Add Patient
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()

    return render(request, 'patients/add_patient.html', {'form': form})


# 👤 Patient Detail
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    wounds = Wound.objects.filter(patient=patient)

    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'wounds': wounds
    })


# 🩺 Add Wound
def add_wound(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = WoundForm(request.POST)
        if form.is_valid():
            wound = form.save(commit=False)
            wound.patient = patient
            wound.save()
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = WoundForm()

    return render(request, 'patients/add_wound.html', {'form': form})


# 🔍 Wound Detail
def wound_detail(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)
    assessments = Assessment.objects.filter(wound=wound)
    images = WoundImage.objects.filter(wound=wound)

    return render(request, 'patients/wound_detail.html', {
        'wound': wound,
        'assessments': assessments,
        'images': images
    })


# 📊 Add Assessment
def add_assessment(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)

    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.wound = wound
            assessment.save()
            return redirect('wound_detail', wound_id=wound.id)
    else:
        form = AssessmentForm()

    return render(request, 'patients/add_assessment.html', {'form': form})


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
        form = WoundImageForm()

    return render(request, 'patients/upload_image.html', {'form': form})




import base64
from django.core.files.base import ContentFile

def camera_capture(request, wound_id):
    wound = get_object_or_404(Wound, id=wound_id)

    if request.method == "POST":
        data = request.POST.get('image_data')

        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]

        file = ContentFile(base64.b64decode(imgstr), name='capture.' + ext)

        image = WoundImage.objects.create(
            wound=wound,
            image=file
        )

        return redirect('wound_detail', wound_id=wound.id)

    return render(request, 'patients/camera.html')


def measure_wound(request, image_id):
    image = get_object_or_404(WoundImage, id=image_id)

    return render(request, 'patients/measure.html', {
        'image': image
    })


def splash(request):
    return render(request, 'splash.html')




from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")  # dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return render(request, "logout.html")



@login_required
def profile(request):
    return render(request, 'profile.html')