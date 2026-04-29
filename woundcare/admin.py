from django.contrib import admin
from .models import Patient, Wound, Assessment, WoundImage


# 👤 Patient Admin (FIXED)
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'surname',
        'gender',
        'date_of_birth',
        'phone',
        'diagnosis'
    )
    search_fields = ('first_name', 'surname', 'phone')


# 🩺 Wound Admin
@admin.register(Wound)
class WoundAdmin(admin.ModelAdmin):
    list_display = ('patient', 'wound_number', 'location', 'date_created')
    list_filter = ('wound_type',)


# 📊 Assessment Admin
from django.contrib import admin
from .models import Assessment

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'wound',
        'wound_type',
        'aetiology',
        'duration',
        'exudate',
        'progression',
        'date_assessed'
    )


# 📷 Wound Image Admin
@admin.register(WoundImage)
class WoundImageAdmin(admin.ModelAdmin):
    list_display = ('wound', 'uploaded_at')




from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Clinical Information'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'get_role', 'get_reg_no', 'is_staff')

    def get_role(self, instance):
        return instance.profile.role
    get_role.short_description = 'Role'

    def get_reg_no(self, instance):
        return instance.profile.registration_number
    get_reg_no.short_description = 'Reg No.'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)