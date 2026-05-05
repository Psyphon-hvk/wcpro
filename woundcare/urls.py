from django.urls import path
from . import views
from .views import login_view, logout_view

urlpatterns = [
    # 🏠 Splash
    path('', views.splash, name='splash'),

    # 📊 Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # 👤 Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('add/', views.add_patient, name='add_patient'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),

    # 🩺 Wounds
    path('add-wound/<int:patient_id>/', views.add_wound, name='add_wound'),
    path('wound/<int:wound_id>/', views.wound_detail, name='wound_detail'),

    # 📊 Assessments
    path('add-assessment/<int:wound_id>/', views.add_assessment, name='add_assessment'),

    # 📷 Images
    path('upload-image/<int:wound_id>/', views.upload_image, name='upload_image'),
    path('camera/<int:wound_id>/', views.camera_capture, name='camera'),
    path('measure/<int:image_id>/', views.measure_wound, name='measure_wound'),

    # 🤝 Sharing & deletion
    path('patient/<int:patient_id>/share/', views.share_patient, name='share_patient'),
    path('patient/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),

    # 🚑 Transfer
    path('patient/<int:patient_id>/transfer/', views.transfer_patient, name='transfer_patient'),

    # 📄 PDF
    path('wound/<int:wound_id>/pdf/', views.wound_pdf, name='wound_pdf'),

    # 🔐 Auth
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]