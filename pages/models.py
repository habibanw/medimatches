from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from .managers import CustomUserManager
from django.template.defaultfilters import slugify
from datetime import timedelta
from django.contrib.postgres.search import SearchVectorField
from django.forms import DateTimeInput

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    def __str__(self):
        return self.email

class Provider(models.Model): 
    provider_id = models.CharField(max_length=10, default='', unique=True)
    firstName = models.CharField(max_length=255, default='')
    lastName = models.CharField(max_length=255, default='')
    gender = models.CharField(max_length=15, default='')
    phone_number = models.CharField(max_length=15, default='')
    specialization = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=100, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    zip_code = models.CharField(max_length=10, default='')
    facility_name = models.CharField(max_length=255, default='', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True) 

    #Methods
    def get_absolute_url(self):
        return reverse('provider-details', kwargs={'pk': self.pk})
    
    def __str__(self):
        return f"{self.firstName} {self.lastName}"
    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_doctor = models.BooleanField(default=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True) #foreign key to the provider class
    info = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_doctor and self.provider:
            self.user.first_name = self.provider.firstName
            self.user.last_name = self.provider.lastName
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email
    
    def get_absolute_url(self):
        return reverse('profile-detail', kwargs={'pk': self.pk})
    
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name="sender", on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name="recipient", on_delete=models.CASCADE)
    subject = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('message-detail',  kwargs={'pk': self.pk})

class Feedback(models.Model):
    patient_user = models.ForeignKey(CustomUser, related_name="patient_user", on_delete=models.DO_NOTHING)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.provider.provider_id

    def get_absolute_url(self):
        return reverse('feedback-detail',  kwargs={'pk': self.pk})

class Appointment(models.Model):
    class Types(models.TextChoices):
        NEW_PATIENT = 'NEW_PATIENT', 'new patient'
        FOLLOW_UP = 'FOLLOW_UP', 'follow up'
        NEW_CONDITION = 'NEW_CONDITION', 'new condition'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    appt_duration = {
        'new patient': 60,
        'follow up': 15,
        'new condition': 30
    }

    patient_user = models.ForeignKey(CustomUser, related_name="patient", on_delete=models.DO_NOTHING)
    provider_user = models.ForeignKey(CustomUser, related_name="provider", on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField()
    type = models.CharField(max_length=100, choices=Types.choices, blank=True)
    canceled = models.BooleanField(default=False)
    canceled_reason = models.TextField(default='')
    status = models.CharField(max_length=20, choices=Status.choices, blank=True)

    @property
    def end_time(self):
        print("type" + self.type)
        length = self.appt_duration.get(self.type)
        return self.start_time + timedelta(minutes=length)
    
    def __str__(self):
        return self.provider_user.last_name + ' ' + self.provider_user.first_name

    def get_absolute_url(self):
        return reverse('appointment-detail',  kwargs={'pk': self.pk})