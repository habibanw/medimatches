from django.test import TestCase
from ..forms import UserRegistrationForm, ProviderRegistrationForm, ProviderIdForm, UserLoginForm, ProviderUpdateForm, UserUpdateForm, FeedbackForm, AppointmentAvailabilityForm
from ..models import Provider


class UserRegistrationFormTest(TestCase):
    def test_user_registration_form_valid(self):
        print("Method: test_user_registration_form.")
        form_data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'password2': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_registration_form_invalid_firstname(self):
        print("Method: test_user_registration_form_invalid_firstname.")
        form_data = {
            'email': 'test@example.com',
            'first_name': '',  # Required field missing
            'last_name': 'Doe',
            'password': 'password123',
            'password2': 'password123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_registration_form_invalid_lastname(self):
        print("Method: test_user_registration_form_invalid_lastname.")
        form_data = {
            'email': 'test@example.com',
            'first_name': 'John',  
            'last_name': '', # Required field missing
            'password': 'password123',
            'password2': 'password123',
        }
        form = UserRegistrationForm(data=form_data) #note: checking if password match is valid is done in views.py
        self.assertFalse(form.is_valid())

    def test_user_registration_form_invalid_password(self):
        print("Method: test_user_registration_form_invalid_password.")
        form_data = {
            'email': 'test@example.com',
            'first_name': 'John',  
            'last_name': 'Doe', 
            'password': '', # Required field missing
            'password2': '',
        }
        form = UserRegistrationForm(data=form_data) 
        self.assertFalse(form.is_valid())
    

class ProviderRegistrationFormTest(TestCase):
    def test_provider_registration_form_valid(self):
        print("Method: test_provider_registration_form_valid.")
        form_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
        }
        form = ProviderRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_provider_registration_form_invalid(self):
        print("Method: test_provider_registration_form_invalid.")
        form_data = {
            'email': '', #no email 
            'password': 'password123',
            'password2': 'password123',
        }
        form = ProviderRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_provider_registration_form_invalid_password(self):
        print("Method: test_provider_registration_form_invalid_password.")
        form_data = {
            'email': 'test@example.com', #no email 
            'password': '',
            'password2': 'password123',
        }
        form = ProviderRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

class ProviderIdFormTest(TestCase):
    def test_provider_id_valid(self):
        print("Method: test_provider_id_form_valid.") 
        form_data = {
            'provider_id': '1114033073'
        }
        form = ProviderIdForm(data=form_data) #note: checking if it is valid is done in views.py
        self.assertTrue(form.is_valid())
    
    def test_provider_id_long(self):
        print("Method: test_provider_id_long.") 
        form_data = {
            'provider_id': '111403307322' #too long
        }
        form = ProviderIdForm(data=form_data) #note: checking if it is valid is done in views.py
        self.assertFalse(form.is_valid())
    
    def test_provider_id_invalid(self):
        print("Method: test_provider_id_invalid.") 
        form_data = {
            'provider_id': '' #empty
        }
        form = ProviderIdForm(data=form_data) #note: checking if it is valid is done in views.py
        self.assertFalse(form.is_valid())

class UserLoginFormTest(TestCase):
    def test_user_login_valid(self):
        print("Method: test_user_login_valid.") 
        form_data = {
            'email': 'test@example.com',
            'password': 'password123',
        }
        form = UserLoginForm(data=form_data) 
        self.assertTrue(form.is_valid())
    
    def test_user_login_missing_password(self):
        print("Method: test_user_login_missing_password.") 
        form_data = {
            'email': 'test@example.com',
            'password': '', # empty
        }
        form = UserLoginForm(data=form_data) 
        self.assertFalse(form.is_valid())
    
    def test_user_login_missing_email(self):
        print("Method: test_user_login_missing_email.") 
        form_data = {
            'email': 'test@example.com',
            'password': '', # empty
        }
        form = UserLoginForm(data=form_data) 
        self.assertFalse(form.is_valid())

class ProfileUpdateFormTest(TestCase):
    def test_provider_update_form_valid(self):
        print("Method: test_provider_update_form_valid.")
        form_data = {
            'provider_id': '1114033073',
            'firstName': 'TAMMY',
            'lastName': 'JONES',
            'gender': 'F',
            'phone_number': '6813423153',
            'specialization': 'CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            'address': '327 MEDICAL PARK DR',
            'city': 'BRIDGEPORT',
            'state': 'WV',
            'zip_code': '263309006',
            'facility_name': 'UNITED HOSPITAL CENTER INC'
        }
        form = ProviderUpdateForm(data=form_data) 
        self.assertTrue(form.is_valid())

class UserUpdateFormTest(TestCase):
    def test_user_update_form_valid(self):
        print("Method: test_user_update_form_valid.")
        form_data = {
            'email': 'test@example.com',
            'firstName': 'TAMMY',
            'lastName': 'JONES',
        }
        form = UserUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_update_form_invalid(self):
        print("Method: test_user_update_form_invalid.")
        form_data = {
            'email': '',
            'firstName': 'TAMMY',
            'lastName': 'JONES',
        }
        form = UserUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_update_form_no_name(self):
        print("Method: test_user_update_form_no_name.")
        form_data = {
            'email': 'test@example.com',
            'firstName': 'TAMMY',
            'lastName': '', # empty
        }
        form = UserUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())

class FeedbackFormTest(TestCase):
    def test_feedback_form_valid(self):
        print("Method: test_feedback_form_valid.")
        form_data = {
            'content': 'Patient had a good visit',
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_feedback_form_invalid(self):
        print("Method: test_feedback_form_invalid.")
        form_data = {
            'content': '', # empty
        }
        form = FeedbackForm(data=form_data)
        self.assertFalse(form.is_valid())

class AppointmentAvailabilityFormTest(TestCase):

    def test_appt_availability_form_valid(self):
        print("Method: test_appt_availability_form_valid.")
        form_data = {
            'patient_FirstName': 'John',
            'patient_LastName': 'Doe',
            'email': 'test@example.com',
            'type': 'new patient',
            'appointment_date': '04/30/2024',
            'appointment_time': '12:30 PM',
            'provider_firstName': 'TAMMY',
            'provider_lastName': 'JONES',
            'services_info': 'regular checkup',
        }
        form = AppointmentAvailabilityForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_appt_availability_form_invalid(self):
        print("Method: test_appt_availability_form_invalid.")
        form_data = {
            'patient_FirstName': 'John',
            'patient_LastName': 'Doe',
            'email': 'test@example.com',
            'type': '', # empty
            'appointment_date': '04/30/2024',
            'appointment_time': '12:30 PM',
            'provider_firstName': 'TAMMY',
            'provider_lastName': 'JONES',
            'services_info': 'regular checkup',
        }
        form = AppointmentAvailabilityForm(data=form_data)
        self.assertFalse(form.is_valid())