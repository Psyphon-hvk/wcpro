from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'diagnosis']



from .models import Wound, Assessment

class WoundForm(forms.ModelForm):
    class Meta:
        model = Wound
        fields = ['wound_number', 'location']


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['length', 'width', 'depth', 'pain_score']




from .models import WoundImage

class WoundImageForm(forms.ModelForm):
    class Meta:
        model = WoundImage
        fields = ['image']