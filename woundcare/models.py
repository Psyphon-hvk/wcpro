from django.db import models


# 👤 Patient Model
class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    diagnosis = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# 🩺 Wound Model
class Wound(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    wound_number = models.IntegerField()
    location = models.CharField(max_length=50)

    # 🔥 Clinical classification
    wound_type = models.CharField(max_length=50, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wound {self.wound_number} - {self.patient.name}"


# 📊 Assessment Model
class Assessment(models.Model):

    EXUDATE_CHOICES = [
        ('none', 'None'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('heavy', 'Heavy'),
    ]

    TISSUE_CHOICES = [
        ('granulation', 'Granulation'),
        ('slough', 'Slough'),
        ('necrosis', 'Necrosis'),
        ('epithelial', 'Epithelial'),
    ]

    wound = models.ForeignKey(Wound, on_delete=models.CASCADE)
    length = models.FloatField()
    width = models.FloatField()
    depth = models.FloatField()

    pain_score = models.IntegerField()

    # 🔥 Clinical fields
    exudate = models.CharField(
        max_length=10,
        choices=EXUDATE_CHOICES,
        default='none'
    )

    infection = models.BooleanField(default=False)

    tissue_type = models.CharField(
        max_length=20,
        choices=TISSUE_CHOICES,
        blank=True,
        null=True
    )

    date_assessed = models.DateTimeField(auto_now_add=True)

    def area(self):
        return self.length * self.width

    def __str__(self):
        return f"Assessment for {self.wound}"


# 📷 Wound Image Model
class WoundImage(models.Model):
    wound = models.ForeignKey(Wound, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='wounds/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.wound}"