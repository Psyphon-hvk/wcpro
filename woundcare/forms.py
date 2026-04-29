from django import forms
from .models import Patient, Wound, Assessment, WoundImage


# 👤 Patient Form (FIXED)
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'surname',
            'gender',
            'date_of_birth',
            'phone',
            'diagnosis'
        ]


# 🩺 Wound Form
class WoundForm(forms.ModelForm):
    class Meta:
        model = Wound
        fields = ['wound_number', 'location']





# 📷 Image Upload Form
class WoundImageForm(forms.ModelForm):
    class Meta:
        model = WoundImage
        fields = ['image']