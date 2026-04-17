from django.urls import path
from django.urls import path
from .views import login_view, logout_view
from . import views

urlpatterns = [
    path('', views.splash, name='splash'),  # ✅ Splash FIRST

    path('dashboard/', views.dashboard, name='dashboard'),

    path('patients/', views.patient_list, name='patient_list'),
    path('add/', views.add_patient, name='add_patient'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('add-wound/<int:patient_id>/', views.add_wound, name='add_wound'),
    path('wound/<int:wound_id>/', views.wound_detail, name='wound_detail'),
    path('add-assessment/<int:wound_id>/', views.add_assessment, name='add_assessment'),
    path('upload-image/<int:wound_id>/', views.upload_image, name='upload_image'),
    path('camera/<int:wound_id>/', views.camera_capture, name='camera'),
    path('measure/<int:image_id>/', views.measure_wound, name='measure_wound'),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('profile/', views.profile, name='profile'),
]