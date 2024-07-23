from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Provider, Profile, Feedback, Appointment, Message
# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    raw_id_fields = ['provider']

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    model = CustomUser
    list_display = ("email", 'first_name', 'last_name', "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
        ('Important dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Create a profile for the user if it doesn't exist
        if not hasattr(obj, 'profile'):
            Profile.objects.create(user=obj)

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'provider']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Provider)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Feedback)
admin.site.register(Appointment)
admin.site.register(Message)
