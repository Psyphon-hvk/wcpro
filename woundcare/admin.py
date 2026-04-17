from django.contrib import admin
from .models import Patient, Wound, Assessment

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'diagnosis')


@admin.register(Wound)
class WoundAdmin(admin.ModelAdmin):
    list_display = ('patient', 'wound_number', 'location', 'date_created')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('wound', 'length', 'width', 'depth', 'pain_score', 'date_assessed')