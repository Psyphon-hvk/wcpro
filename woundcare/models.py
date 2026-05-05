from django.db import models
from django.contrib.auth.models import User
from datetime import date


# 👤 Patient Model
class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients", null=True, blank=True)
    first_name = models.CharField(max_length=100, default="")
    surname = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=10, default="unknown")

    date_of_birth = models.DateField(null=True, blank=True)

    reg_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    phone = models.CharField(max_length=15, blank=True, null=True)
    diagnosis = models.CharField(max_length=100, blank=True, null=True)

    # Health info fields
    general_factors   = models.TextField(blank=True, null=True)
    metabolic_factors = models.TextField(blank=True, null=True)
    pathologies       = models.TextField(blank=True, null=True)
    surgical_history  = models.TextField(blank=True, null=True)
    allergies         = models.TextField(blank=True, null=True)
    medication        = models.TextField(blank=True, null=True)
    compliance        = models.TextField(blank=True, null=True)
    additional_info   = models.TextField(blank=True, null=True)

    consent_given = models.BooleanField(default=False)

    # ── Transfer / location tracking ──────────────────────────────
    STATUS_INPATIENT   = 'inpatient'
    STATUS_OUTPATIENT  = 'outpatient'
    STATUS_CHOICES = [
        (STATUS_INPATIENT,  'Inpatient'),
        (STATUS_OUTPATIENT, 'Outpatient'),
    ]
    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OUTPATIENT,
    )
    current_ward = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ward name / number when inpatient; blank when outpatient.",
    )
    # ──────────────────────────────────────────────────────────────

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            d = self.date_of_birth
            return today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        return None

    def __str__(self):
        return f"{self.first_name} {self.surname}"


# 🩺 Wound Model
class Wound(models.Model):
    patient     = models.ForeignKey(Patient, on_delete=models.CASCADE)
    wound_number = models.IntegerField()
    location    = models.CharField(max_length=50)
    wound_type  = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wound {self.wound_number} - {self.patient.first_name}"


# 📊 Assessment Model
class Assessment(models.Model):
    wound = models.ForeignKey(Wound, on_delete=models.CASCADE)

    wound_type       = models.CharField(max_length=100, blank=True, null=True)
    aetiology        = models.CharField(max_length=100, blank=True, null=True)
    duration         = models.CharField(max_length=100, blank=True, null=True)

    margins          = models.CharField(max_length=100, blank=True, null=True)
    surrounding_skin = models.CharField(max_length=100, blank=True, null=True)
    exudate          = models.CharField(max_length=20,  blank=True, null=True)

    progression = models.CharField(max_length=50, blank=True, null=True)
    notes       = models.TextField(blank=True, null=True)

    tissue_epithelial  = models.IntegerField(default=0)
    tissue_granulation = models.IntegerField(default=0)
    tissue_slough      = models.IntegerField(default=0)
    tissue_necrosis    = models.IntegerField(default=0)

    date_assessed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment for {self.wound}"


# 📷 Wound Image Model
class WoundImage(models.Model):
    wound       = models.ForeignKey(Wound, on_delete=models.CASCADE)
    image       = models.ImageField(upload_to='wounds/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.wound}"


# 👤 Profile Model
class Profile(models.Model):
    ROLE_CHOICES = [
        ('surgeon', 'Surgeon'),
        ('doctor',  'Doctor'),
        ('nurse',   'Nurse'),
        ('guest',   'Guest'),
    ]

    user                = models.OneToOneField(User, on_delete=models.CASCADE)
    role                = models.CharField(max_length=20, choices=ROLE_CHOICES)
    registration_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# 🔗 Patient Access (sharing)
class PatientAccess(models.Model):
    patient    = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="access_list")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_patients")
    can_edit   = models.BooleanField(default=False)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="granted_access",
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'user')

    def __str__(self):
        return f"{self.patient} shared with {self.user.username}"


# 🚑 Patient Transfer Log
class PatientTransfer(models.Model):
    TYPE_WARD_TO_WARD        = 'ward_to_ward'
    TYPE_WARD_TO_OUTPATIENT  = 'ward_to_outpatient'
    TYPE_OUTPATIENT_TO_WARD  = 'outpatient_to_ward'

    TRANSFER_TYPE_CHOICES = [
        (TYPE_WARD_TO_WARD,       'Ward → Ward'),
        (TYPE_WARD_TO_OUTPATIENT, 'Ward → Outpatient (Discharge)'),
        (TYPE_OUTPATIENT_TO_WARD, 'Outpatient → Ward (Admission)'),
    ]

    patient       = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='transfers')
    performed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_performed')
    transfer_type = models.CharField(max_length=30, choices=TRANSFER_TYPE_CHOICES)
    from_location = models.CharField(max_length=100)   # ward name or "Outpatient"
    to_location   = models.CharField(max_length=100)   # ward name or "Outpatient"
    notes         = models.TextField(blank=True, null=True)
    transferred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transferred_at']

    def __str__(self):
        return f"{self.patient} | {self.get_transfer_type_display()} @ {self.transferred_at:%Y-%m-%d %H:%M}"