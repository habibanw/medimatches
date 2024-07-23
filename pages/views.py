from typing import Any
from django.db.models.query import QuerySet
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from .forms import UserRegistrationForm, UserLoginForm, ProviderRegistrationForm, ProviderIdForm, ProviderUpdateForm, ProviderSearchForm, UserUpdateForm, FeedbackForm, SendMessageForm, AppointmentAvailabilityForm, SpecialistSuggesterForm, ContactUsForm
from .models import Provider, Profile, Appointment, CustomUser, Message
from .services import get_nearby_zip_codes, get_zipcodes_from_city_state
from django.contrib import messages
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import require_GET
from django.http import HttpResponse, JsonResponse
from django.contrib.postgres.search import SearchQuery
from functools import reduce
from operator import or_
from django.db.models import Q, Case, When, Value, BooleanField
from django.contrib.postgres.search import SearchQuery
from datetime import datetime, timedelta
from openai import OpenAI
import os
import openai
from django.core.mail import send_mail

# Create your views here.

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)


def index(request):
    return render(request, 'core/index.html')

def about(request):
    return render(request, 'core/about.html')


def services(request):
    return render(request, 'core/services.html')


def faq(request):
    return render(request, 'core/faq.html')

def profile(request):
    return render(request, 'core/profile.html')

def no_provider_id(request):
    return render(request, 'error/no_provider_id.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def register_choose_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'provider':
            return redirect('check_provider_id')
        else:
            return redirect('create_user_account')
    return render(request, 'account/choose_role.html')

def check_provider_id(request):
    if request.method == 'POST':
        form = ProviderIdForm(request.POST)
        if form.is_valid():
            provider_id = form.cleaned_data['provider_id']
            if Provider.objects.filter(provider_id=provider_id).exists():
                request.session['provider_id'] = provider_id
                return redirect('create_provider_account')
            else:
                messages.error(request, f"There is no provider record associated with that id.")
                return redirect('no_provider_id') 
    else:
        form = ProviderIdForm()
    return render(request, 'account/check_provider_id.html', {'form': form})

def create_provider_account(request):
    form = ProviderRegistrationForm()
    if request.method == 'POST':
        provider_id = request.session.get('provider_id') #gets provider id from session
        if provider_id: # if provider id exists
            form = ProviderRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                # Set the user's password securely
                email = form.cleaned_data['email']         
                password1 = form.cleaned_data['password']
                password2 = form.cleaned_data['password2']
                if password1 == password2:
                    user.set_password(password1)
                    provider=Provider.objects.get(provider_id=provider_id)
                    user.first_name = provider.firstName #just in case 
                    user.last_name = provider.lastName
                    user.save()
                    profile = Profile.objects.create(user=user, is_doctor=True, provider=Provider.objects.get(provider_id=provider_id))
                    messages.success(request, f'Your Account has been created {profile.provider.firstName} {profile.provider.lastName}!')
                    #return redirect('profile') #temporary

                    user = authenticate(request, email=email, password=password1)
                    if user is not None:
                        login(request, user)
                        # Redirect to a success page
                        messages.success(request, f'Welcome {user.first_name} {user.last_name}!')
                        return redirect('index') #temporary  
                    else:
                        messages.error(request, 'Authenication Failure')
                else:
                    # Handle password mismatch error here
                    form.add_error('password2', 'Passwords entered do not match')
            else:
                if 'email' in form.errors and 'User with this Email already exists.' in form.errors['email']:
                    found_user = CustomUser.objects.filter(email=form.data['email']).first()
                    provider=Provider.objects.get(provider_id=provider_id)
                    if found_user and provider.firstName == found_user.first_name and provider.lastName == found_user.last_name and found_user.is_active == False:
                        messages.error(request, 'Your account has been deactivated. Please contact us to re-activate it.')
                    elif found_user and provider.firstName == found_user.first_name and provider.lastName == found_user.last_name:
                        messages.error(request, 'An account with this email already exists. Please log in.')
                    else:
                        messages.error(request, 'User already exists.')
                        print('User already exists')
        else:
            messages.error(request, f'No Provider id was provided')
            return redirect('check_provider_id')
    return render(request, 'account/create_provider_account.html', {'form': form})

def create_user_account(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set the user's password securely
            email = form.cleaned_data['email']         
            password1 = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            if password1 == password2:
                user.set_password(password1)
                #user.is_doctor = False
                user.save()
                profile = Profile.objects.create(user=user, is_doctor=False)
                messages.success(request, f'Your Account has been created {profile.user.first_name} {profile.user.last_name}!')
                user = authenticate(request, email=email, password=password1)
                if user is not None:
                    login(request, user)
                    # Redirect to a success page
                    messages.success(request, f'Welcome {user.first_name} {user.last_name}!')
                    return redirect('index') #temporary  
                else:
                    messages.error(request, 'Authenication Failure')
            else:
                # Handle password mismatch error here
                form.add_error('password2', 'Passwords entered do not match')
        else:
            if 'email' in form.errors and 'User with this Email already exists.' in form.errors['email']:
                found_user = CustomUser.objects.filter(email=form.data['email']).first()
                if found_user and form.cleaned_data['first_name'] == found_user.first_name and form.cleaned_data['last_name'] == found_user.last_name and found_user.is_active == False:
                        messages.error(request, 'Your account has been deactivated. Please contact us to re-activate it.')
                elif found_user and form.cleaned_data['first_name'] == found_user.first_name and form.cleaned_data['last_name'] == found_user.last_name:
                    messages.error(request, 'An account with this email already exists. Please log in.')
                else:
                    messages.error(request, 'User already exists.')
                    print('User already exists')
               # return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'account/create_user_account.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page
                messages.success(request, f'Welcome {user.first_name} {user.last_name}!')
                return redirect('profile') #temporary
            else:
                messages.error(request, f'Incorrect email or password!')
                #return redirect('invalid')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def provider_update(request):
    # Load the currently logged in user
    user = request.user

    if user.id != None:
        # Load the currently logged in user
        user = request.user
        
        # Get the user's profile
        profile  = Profile.objects.filter(user_id=request.user.pk).first()
        
        if profile and profile.is_doctor == True:
            # Get the provider object for this user
            provider = Provider.objects.filter(pk=profile.provider_id).first()
            if provider:
                form = ProviderUpdateForm(request.POST if request.POST else None, instance = provider)
       
                if request.method == 'POST':
                    if form.is_valid():
                        form.save()
                        messages.success(request, f'Updates saved successfully')
        
                return render(request, 'account/provider_update.html', {'form': form, 'user': user, 'profile': profile, 'provider': provider})
        
            else: 
                messages.error(request, f"There is no provider record associated with this user's profile")
                return render(request, '403.html')
            
        else: 
            messages.error(request, f"You do not have access to this page")
            return render(request, '403.html')
    
    else:
        messages.error(request, f"You must log in to update your profile")
        return redirect('login')

class ProviderListView(generic.ListView):
    model = Provider
    paginate_by = 50
    template_name = 'core/provider_list.html'

    def get_queryset(self) -> QuerySet[Any]:
        # if this a full-text search?
        search_string = self.request.GET.get('keywords', '')

        if search_string:
            query = SearchQuery(search_string)
        
        # We are just doing a keyword search from the header search bar
        if search_string and len(self.request.GET.keys()) == 1:
            return Provider.objects.filter(search_vector=query).exclude(lastName__exact='')
        
        else:
            queryset = Provider.objects.all()
            form = ProviderSearchForm(self.request.GET)
            if form.is_valid():
                name_query = form.cleaned_data.get('name_query')
                gender = form.cleaned_data.get('gender')
                specialization = form.cleaned_data.get('specialization')
                city = form.cleaned_data.get('city')
                state = form.cleaned_data.get('state')
                zip_code = form.cleaned_data.get('zip_code')
                facility_name = form.cleaned_data.get('facility_name')

                if search_string:
                    queryset = queryset.filter(search_vector=query)    
            
                if name_query:
                    names = name_query.split(' ')
                    if len(names) == 2:
                        queryset = queryset.filter(lastName__icontains=names[1], firstName__icontains=names[0]) | queryset.filter(lastName__icontains=names[0], firstName__icontains=names[1])
                    else:
                        queryset = queryset.filter(lastName__icontains=name_query) | queryset.filter(firstName__icontains=name_query)
                if gender:
                    queryset = queryset.filter(gender=gender)
                if specialization:
                    queryset = queryset.filter(specialization__icontains=specialization)
                """
                We are doing some proximity searching. The logic is:

                If we have city and state, but not zip code:
                    Look up a list of zip codes that match the city and state and use those for searching.
                    If the API fails to give a response, go ahead and string match city and state. 
                
                If we have a zip code (and even if we also have city and state):
                    Look up a list of nearby zip codes within a 15-mile radius and search with that.
                    ignoring the city and state strings. 
                    If the API fails, string match with the zip code the user entered. 
                """
                
                if city and state and not zip_code:
                    zip_list = get_zipcodes_from_city_state(city, state)
                    if len(zip_list) > 0:
                        query = reduce(or_, (Q(zip_code__startswith=item) for item in zip_list))
                        queryset = queryset.filter(query)

                        # queryset = queryset.filter(zip_code__in=zip_list)
                    else: 
                        queryset = queryset.filter(city__icontains=city)
                        queryset = queryset.filter(state__icontains=state)
                else:
                    if city:
                        queryset = queryset.filter(city__icontains=city)
                    
                    if state:
                        queryset = queryset.filter(state__icontains=state)
                
                if zip_code:
                    zip_list = get_nearby_zip_codes(zip_code)
                    query = reduce(or_, (Q(zip_code__startswith=item) for item in zip_list))
                    queryset = queryset.filter(query)

                    # queryset = queryset.filter(zip_code__in=zip_list)
                if facility_name:
                    queryset = queryset.filter(facility_name__icontains=facility_name)
                
                queryset = queryset.exclude(lastName__exact='')

            return queryset.order_by('lastName', 'firstName')
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ProviderListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        form = ProviderSearchForm(self.request.GET)
        context['total_providers'] = Provider.objects.count() if not form.is_valid() else self.get_queryset().count()
        context['search_form'] = form
        return context

class ProviderDetailView(generic.DetailView):
    model = Provider
    template_name = 'core/provider_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Check if the user is logged in and is not a doctor
        if user.is_authenticated and not user.profile.is_doctor:
            context['feedback_form'] = FeedbackForm()

        provider_obj = self.get_object()

        if Profile.objects.filter(provider=provider_obj).exists():
            context['provider_has_user'] = True
        else:
            context['provider_has_user'] = False

        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        # Ensure the user is not a doctor before processing feedback
        if not user.profile.is_doctor:
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save(commit=False)
                feedback.provider = self.get_object()
                feedback.patient_user = request.user
                feedback.save()
                messages.success(request, 'Your feedback has been submitted successfully.')
                return redirect('provider-details', pk=self.get_object().pk)
            else:
                context = self.get_context_data(feedback_form=form)
                messages.error(request, 'There was an error submitting your feedback. Please try again.')
                return self.render_to_response(context)
        else:
            messages.error(request, 'Providers cannot submit feedback.')
            return redirect('provider-details', pk=self.get_object().pk)
    
def delete_account(request):
    # Load the currently logged in user
    user = request.user

    if user.id != None:
        if request.method == 'POST':
            user = request.user
            # Get the user's profile
            profile  = Profile.objects.filter(user_id=request.user.pk).first()
            if profile:
                if profile.is_doctor == True:
                    appointments_to_cancel = Appointment.objects.filter(provider_user_id=user.pk, canceled=False, start_time__gte=timezone.now())
                    if appointments_to_cancel:
                        patient_users = set()
                        for appointment in appointments_to_cancel:
                            appointment.canceled = True
                            appointment.canceled_reason = "Provider account deactivated/deleted"
                            appointment.save()

                            patient_users.add(appointment.patient_user)
                        
                        for patient_user in patient_users:
                            # Send message to patients
                            Message.objects.create(
                            sender=request.user,
                            recipient=patient_user,
                            subject=f'Appointment Cancelation',
                            content= f'All appointments associated with {request.user.first_name} {request.user.last_name} have been canceled due to account deactivation.'
                            )
                else:
                    appointments_to_cancel = Appointment.objects.filter(patient_user_id=user.pk, canceled=False, start_time__gte=timezone.now())
                    if appointments_to_cancel:
                        provider_users = set()
                        for appointment in appointments_to_cancel:
                            appointment.canceled = True
                            appointment.canceled_reason = "Patient account deactivated/deleted"
                            appointment.save()

                            provider_users.add(appointment.provider_user)
                        
                        for provider_user in provider_users:
                            # Send message to provider
                            Message.objects.create(
                            sender=request.user,
                            recipient=provider_user,
                            subject=f'Appointment Cancelation',
                            content= f'All appointments associated with {request.user.first_name} {request.user.last_name} have been canceled due to account deactivation.'
                            )
                user.is_active = False
                user.save()
                logout(request) #Log out the user after account deletion
                messages.success(request, f'Account deleted successfully')
                return redirect('index')
    else:
        messages.error(request, f"You must log in to delete your account")
        return redirect('login')
    return render(request, 'account/delete_account.html')


def user_update(request):
    # Load the currently logged in user
    user = request.user

    if user.id != None:
        # Get the user's profile
        profile = Profile.objects.filter(user_id=request.user.pk).first()
        provider = Provider.objects.filter(pk=user.pk).first()
        custom_user = CustomUser.objects.filter(pk=user.pk).first()

        if custom_user:
            form = UserUpdateForm(request.POST if request.POST else None, instance=user)

            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Updates saved successfully')
                    redirect('profile')

            return render(request, 'account/user_update.html',
                              {'form': form, 'user': user, 'profile': profile, 'provider': provider})
        elif provider:
            form = UserUpdateForm(request.POST if request.POST else None, instance=provider)

            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Updates saved successfully')
            return render(request, 'account/user_update.html',
                          {'form': form, 'user': user, 'profile': profile, 'provider': provider})
        # form = UserUpdateForm()

        # if request.method == 'POST':
        #     if form.is_valid():
        #         form.save()
        #         messages.success(request, f'Updates saved successfully')
        #
        # return render(request, 'account/user_update.html',
        #                        {'form': form, 'user': user, 'profile': profile})
        else:
            messages.error(request, f"There is no user record associated with this user's profile")
            return render(request, '403.html')

    else:
        messages.error(request, f"You do not have access to this page")
        return render(request, '403.html')
    # else:
    #     messages.error(request, f"You must log in to update your profile")
    #     return redirect('login')

def feedback(request):
    # Load the currently logged in user
    user = request.user

    if user.id != None:
        # Load the currently logged in user
        user = request.user

        # Get the user's profile
        profile = Profile.objects.filter(user_id=request.user.pk).first()
        # Get the provider object for this user
        provider = Provider.objects.filter(pk=user.pk).first()
        custom_user = CustomUser.objects.filter(pk=user.pk).first()

        if provider:
            form = FeedbackForm(request.POST if request.POST else None, instance = provider)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Feedback saved successfully')
            return render(request, 'account/feedback.html', {'form': FeedbackForm})

        elif custom_user:
            form = FeedbackForm(request.POST if request.POST else None, instance=user)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Feedback saved successfully')
            return render(request, 'account/feedback.html', {'form': FeedbackForm})
        else:
            messages.error(request, f"You do not have access to this page")
            return render(request, '403.html')
    else:
        messages.error(request, f"You must log in to update your profile")
        return redirect('login')
####

@login_required
def profile_view(request):
    context = {}
    try:
        user_profile = Profile.objects.get(user=request.user)
        context['profile'] = user_profile
        if user_profile.is_doctor:
            # Additional context for providers
            context['provider_details'] = get_object_or_404(Provider, pk=user_profile.provider.pk)
    except Profile.DoesNotExist:
        context['error'] = 'Profile does not exist.'
    return render(request, 'core/profile.html', context)

def create_message(request, id):
    # User must be logged in to send messages
    if request.user.is_authenticated == False:
        messages.error(request, f"You must log in to send a message.")
        return redirect('login')

    # Don't send messages to non-existent providers
    try:
        provider = Provider.objects.get(pk=id)
    except Provider.DoesNotExist:
        messages.error(request, f"There is no provider record associated with this profile.")
        return render(request, 'invalid.html')
    
    # Provider must have a profile/user in order to receive messages 
    try:
        provider_profile = Profile.objects.get(provider=id)
    except Profile.DoesNotExist:
        messages.error(request, "This provider has not claimed their profile and MediMatch and cannot receive messages.")
        return redirect('/providers/' + str(provider.pk))
    
    recipient = CustomUser.objects.get(pk=provider_profile.user.pk)
    
    # Providers can't send messages to themselves
    if request.user.pk == recipient.pk:
        messages.error(request, f"You cannot send a message to yourself.")
        return redirect('/providers/' + str(provider.pk))
    
    found_user = CustomUser.objects.filter(email=provider_profile.user.email).first()
    if found_user and found_user.is_active == False:
        messages.error(request, 'This provider has deactivated their account. Please contact us for more information.')
        return redirect('/providers/' + str(provider.pk))

    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Message sent successfully')
    else:
        form = SendMessageForm(initial={'recipient': recipient.pk, 'sender': request.user.pk})
        
    return render(request, 'core/send_message.html', {'form': form, 'provider': provider})

class MessagesListView(LoginRequiredMixin,generic.ListView):
    login_url = '/login'
    model = Message
    paginate_by = 50
    template_name = 'account/message_list.html'

    def get_queryset(self):
        return Message.objects.filter(recipient_id=self.request.user.pk).order_by('-created_at')
    
def request_appointment(request, id):

    # User must be logged in to schedule appointment
    if request.user.is_authenticated == False:
        messages.error(request, f"You must log in to schedule an appointment.")
        return redirect('login')

    # Don't schedule appointments to non-existent providers
    try:
        provider = Provider.objects.get(pk=id)
    except Provider.DoesNotExist:
        messages.error(request, f"There is no provider record associated with this profile.")
        return render(request, 'invalid.html')
    
    # Provider must have a profile/user in order to receive messages for appt
    try:
        provider_profile = Profile.objects.get(provider=id)
    except Profile.DoesNotExist:
        messages.error(request, "This provider has not claimed their profile and MediMatch and cannot receive messages.")
        return redirect('/providers/' + str(provider.pk))
    
    apptProvider = CustomUser.objects.get(pk=provider_profile.user.pk)

    # Providers can't schedule appt to themselves
    if request.user.pk == apptProvider.pk:
        messages.error(request, f"You cannot schedule appointment to yourself.")
        return redirect('/providers/' + str(provider.pk))
    
    found_user = CustomUser.objects.filter(email=provider_profile.user.email).first()
    if found_user and found_user.is_active == False:
        messages.error(request, 'This provider has deactivated their account. Please contact us for more information.')
        return redirect('/providers/' + str(provider.pk))
    
    # Prefill the form with the provider's information
    initial_data = {
        'provider_firstName': provider.firstName,
        'provider_lastName': provider.lastName,
        'patient_firstName': request.user.first_name,
        'patient_lastName': request.user.last_name,
        'email': request.user.email,
    }

    if request.method == 'POST':
        if apptProvider:
            form = AppointmentAvailabilityForm(request.POST)
            if form.is_valid():
                # Check if the appointment time is available
                appointment_date = form.cleaned_data['appointment_date']
                appointment_time = form.cleaned_data['appointment_time']
                appointment_starttime = datetime.combine(appointment_date, appointment_time)
                appointment_type = form.cleaned_data['type']
                appointment_duration = Appointment.appt_duration.get(appointment_type)
                appointment_endtime = appointment_starttime + timedelta(minutes=appointment_duration)
                # check if the appointment time is available -> note: lte = less than or equal to, gt = greater than => part of Django Object Relational Mapping (ORM)
                existing_appointments = Appointment.objects.filter(provider_user=apptProvider, #filters based on provider
                                                                   start_time__date=appointment_starttime.date(), #filters for appt on same date
                                                                     start_time__lt=appointment_endtime,
                                                                     start_time__gt=(appointment_starttime - timedelta(minutes=appointment_duration)),
                                                                     status__in=[Appointment.Status.PENDING, Appointment.Status.APPROVED],
                                                                     canceled=False 
                                                                     ) 
                if existing_appointments.exists():
                    messages.error(request, f'The appointment slot is not available.')
                else:

                    if timezone.make_aware(datetime.combine(appointment_date, appointment_time)) < timezone.now():
                        messages.error(request, f'You can only schedule appointments for future dates.')
                    else:
                        # Create the appointment object
                        appointment = Appointment.objects.create(
                            provider_user=apptProvider,
                            patient_user=request.user,
                            start_time=appointment_starttime,
                            type=form.cleaned_data['type'],
                            status='pending'
                        )

                        message_content = f' {request.user.first_name} {request.user.last_name} has requested an appointment on {appointment_starttime}.<br>'
                        message_content += f' Please approve or deny the request.<br>'
                        message_content += f' <a href="/appointments/appt_detail/{appointment.pk}" style="text-decoration: underline;">Click here</a> to view appointment details.<br>'

                        # Send message to provider
                        Message.objects.create(
                            sender=request.user,
                            recipient=apptProvider,
                            subject=f'Appointment Request',
                            content=message_content
                        )
                        messages.success(request, f'Appointment requested successfully')
                        return redirect('appointment-details', pk=appointment.pk)
            else:
                messages.error(request, f'Invalid form data')
    else:
        form = AppointmentAvailabilityForm(initial=initial_data)

    return render(request, 'core/schedule_appt.html', {'form': form, 'provider': provider})

def appointment_status_update(request, pk):  
    # User must be logged in to approve appointment
    if request.method == 'POST':

        if request.user.is_authenticated == False:
            messages.error(request, f"You must log in to approve an appointment.")
            return redirect('login')
        
        user_type = Profile.objects.get(user=request.user)
        if user_type.is_doctor == True:

            appointment = Appointment.objects.get(pk=pk)
            status = request.POST.get('status')
            if appointment != None:
                if status == 'approved':
                    apptProvider = appointment.provider_user
                    appointment.status = "approved"
                    appointment.save() 

                    message_content = f' {apptProvider.first_name} {apptProvider.last_name} has approved an appointment on {appointment.start_time}.<br>'
                    message_content += f' <a href="/appointments/appt_detail/{appointment.pk}" style="text-decoration: underline;">Click here</a> to view appointment details.<br>'

                    # Send message to patient
                    Message.objects.create(
                        sender=apptProvider,
                        recipient=appointment.patient_user,
                        subject=f'Appointment Approved',
                        content= message_content
                    )
                    return JsonResponse({'success': True})
                
                elif status == 'rejected':
                    apptProvider = appointment.provider_user
                    appointment.canceled = True
                    appointment.canceled_reason = "Provider rejected appointment"
                    appointment.status = "rejected"
                    appointment.save()

                    message_content = f' {apptProvider.first_name} {apptProvider.last_name} has rejected an appointment on {appointment.start_time}.<br>'
                    message_content += f' <a href="/appointments/appt_detail/{appointment.pk}" style="text-decoration: underline;">Click here</a> to view appointment details.<br>'

                    # Send message to patient
                    Message.objects.create(
                        sender=apptProvider,
                        recipient=appointment.patient_user,
                        subject=f'Appointment Rejected',
                        content= message_content
                    )
                    return JsonResponse({'success': True})
            else:
                messages.error(request, f"There is no appointment record associated with this profile.")
                return render(request, 'invalid.html') 
        else:
            messages.error(request, f"You do not have access to this page")
            return render(request, 'invalid.html')


class AppointmentDetailView(generic.DetailView):
    model = Appointment
    template_name = 'core/appt_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AppointmentDetailView, self).get_context_data(**kwargs)
        appt_obj = self.get_object()

        if Appointment.objects.filter(pk=appt_obj.pk).exists():
            context['appointment_exists'] = True
        else:
            context['appointment_no_exists'] = False
        return context
    
class AppointmentsListView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    model = Appointment
    template_name = 'account/appt_list.html'
    paginate_by = 10

    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if(user_profile.is_doctor):
            query_set = Appointment.objects.filter(provider_user_id=self.request.user.pk)
        else:
            query_set = Appointment.objects.filter(patient_user_id=self.request.user.pk)
        
        query_set = query_set.annotate(
            canceled_last=Case(
                When(canceled=True, then=Value(1)),
                default=Value(0),
                output_field=BooleanField(),
            ),
        ).order_by('canceled_last', '-start_time')

        return query_set

    def get_context_data(self, **kwargs):
        context = super(AppointmentsListView, self).get_context_data(**kwargs)
        context['total_appointments'] = Appointment.objects.filter(patient_user_id=self.request.user.pk).count()
        return context

def message_delete(request, id):
     # User must be logged in to delete messages
    if request.user.is_authenticated == False:
        messages.error(request, f"You must log in to delete a message.")
        return redirect('login')
    
    # Don't delete non-existing messages
    try:
        message = Message.objects.get(pk=id)

    except Message.DoesNotExist:
        messages.error(request, f"That message does not exist.")
        return render(request, 'invalid.html')
    
    # make sure the current user is the recipient of the message
    if request.user.pk == message.recipient_id:
        # delete message
        instance = Message.objects.get(pk=id)
        instance.delete()
        messages.success(request, f"Message has been deleted.")
    else:
        messages.error(request, f"You are not authorized to delete this message.")
    
    return redirect('messages')

def message_is_read(request, id):
    message = Message.objects.get(pk=id)
    message.is_read = True
    message.save()
    return JsonResponse({'success': True})


def reply_message(request, id):
    if request.user.is_authenticated == False:
        messages.error(request, f"You must log in to send a message.")
        return redirect('login')
    
    try:
        original_message = Message.objects.get(pk=id)
    except Message.DoesNotExist:
        messages.error(request, f"That message you are trying to reply to does not exist.")
        return render(request, 'invalid.html')
    
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            form.instance.recipient = original_message.sender
            form.instance.sender = request.user
            form.save()
            messages.success(request, f'Reply sent successfully')
            return redirect('messages')
    else:
        # Set initial data for reply with the subject and with the "Re: " and prevent duplicate "Re: Re: " in the subject
        if original_message.subject.startswith("Re: "):
            initial_subject = original_message.subject
        else:
            initial_subject = f"Re: {original_message.subject}"
        form = SendMessageForm(initial={'recipient': original_message.sender.pk, 'sender': request.user.pk, 'subject': initial_subject})

    return render(request, 'core/reply_message.html', {'form': form, 'original_message': original_message})

def symptom_suggester(request):
    form = SpecialistSuggesterForm()
    
    # User must be logged in
    if request.user.is_authenticated == False:
        messages.error(request, f"This feature is only available to logged in users.")
        return redirect('login')

    if request.method == 'POST':
        form = SpecialistSuggesterForm(request.POST)
        if form.is_valid():
            # open ai stuff goes here
            symptom_list = request.POST.getlist('symptoms')
            symptom_string = ', ' . join(symptom_list) 
            prompt = f"""
                I am a medical patient experiencing the following list of symptoms: {symptom_string}.
                
                What kind of doctor should I seek for treatment?"""            
            try:
                response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    )
                #get response
                bot_response = response.choices[0].message.content
                return render(request, 'core/symptom_suggester.html', {'form': form, 'bot_response': bot_response, 'prompt': prompt})
             
            except openai.APIConnectionError as e:
                #Handle connection error here
                messages.warning(request, f"Failed to connect to OpenAI API, check your internet connection")
            except openai.RateLimitError as e:
                #Handle rate limit error (we recommend using exponential backoff)
                messages.warning(request, f"You exceeded your current quota, please check your plan and billing details.")
    
    return render(request, 'core/symptom_suggester.html', {'form': form})

def cancel_appt(request, pk):
    if request.method == 'POST':
        # User must be logged in to cancel appointment
        if request.user.is_authenticated == False:
            messages.error(request, f"You must log in to cancel an appointment.")
            return redirect('login')
        
        # Don't cancel non-existing appointments
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            messages.error(request, f"That appointment does not exist.")
            return render(request, 'invalid.html')


        if appointment.start_time < timezone.now():
            return JsonResponse({'success': False, 'error_message': 'past_appointment'})

        # make sure the current user is the patient of the appointment or the provider
        if request.user.pk == appointment.patient_user_id or request.user.pk == appointment.provider_user_id:
        
            # cancel appointment
            appointment.canceled = True
            appointment.canceled_reason = f"{request.user.first_name} {request.user.last_name} canceled appointment"
            appointment.save()

            message_content = f' {request.user.first_name} {request.user.last_name} has canceled an appointment on {appointment.start_time}.<br>'
            message_content += f' <a href="/appointments/appt_detail/{appointment.pk}" style="text-decoration: underline;">Click here</a> to view appointment details.<br>'

            if request.user.pk == appointment.patient_user_id:
                # Send message to provider
                Message.objects.create(
                    sender=request.user,
                    recipient=appointment.provider_user,
                    subject=f'Appointment Cancelation',
                    content= message_content
                    )
            else:
                # Send message to patient
                Message.objects.create(
                    sender=request.user,
                    recipient=appointment.patient_user,
                    subject=f'Appointment Cancelation',
                    content= message_content
                    )
            return JsonResponse({'success': True})
        else:
            messages.error(request, f"You do not have access to this page")
            return render(request, 'invalid.html')
    else:
        return render(request, 'invalid.html')
    
def contact_us(request):
    form = ContactUsForm()

    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            send_mail('Contact Us Submission', 'You have received the following message from ' + form.cleaned_data['name'] + '\n\n'  + form.cleaned_data['message'], form.cleaned_data['email'], ['lenguyen.sarah@gmail.com'])
            messages.success(request, f"Your message has been sent successfully.")
        else: 
            messages.error(request, f"We were unable to send your message. Please try again. ")

    return render(request, 'core/contact.html', context={'form': form})