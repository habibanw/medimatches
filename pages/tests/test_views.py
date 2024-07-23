from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from ..models import CustomUser, Profile, Provider, Appointment, Message
from django.utils import timezone
from datetime import timedelta
import warnings
import json

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_role(self):
        print("Method: test_register_role.")
        url = reverse('register_choose_role')
        
        # Mimic user selecting the provider role
        provider_data = {'role': 'provider'}
        provider_response = self.client.post(url, provider_data, follow=True)
        self.assertEqual(provider_response.status_code, 200)
       # self.assertRedirects(provider_response, reverse('check_provider_id'))

        # Mimic user selecting the regular user role
        regular_user_data = {'role': 'regular_user'}
        regular_user_response = self.client.post(url, regular_user_data, follow=True)
        self.assertEqual(regular_user_response.status_code, 200)

    def test_check_provider_id(self):
        print("Method: test_check_provider_id")
        url = reverse('check_provider_id')
        provider_id = {'provider_id': '1234567891'} #invalid
        #follow=true ensures client redirects correctly to the appropriate url
        invalid_response = self.client.post(url, provider_id, follow=True) 
        self.assertEqual(invalid_response.status_code, 200)

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

    def test_create_user_account(self):
        print("Method: test_create_user_account.")
        
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        #self.assertEqual(response.status_code, 200)  # Assuming a successful POST request
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_create_user_account_mismatch_passwords(self):
        print("Method: test_create_user_account_mismatch_passwords.")
        
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password124!', #mismatch passwords
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context['form'] #checking the error thrown by the form
        self.assertIn('password2', form.errors.keys())  # Check if 'password2' is in the errors
        self.assertIn("Passwords entered do not match", form.errors['password2'][0])  # Check for the specific error message

    def test_create_provider_account(self):
        print("Method: test_create_provider_account.")
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)
        #above code is to set up the provider id such that it exists in session

        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, self.provider.firstName) #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, self.provider.lastName)
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=True).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_create_provider_account_missing_id(self):
        print("Method: test_create_provider_account_missing_id")
        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'No Provider id was provided')

    
    def test_create_provider_account_mismatch_passwords(self):
        print("Method: test_create_provider_account_mismatch_passwords")
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)
        #above code is to set up the provider id such that it exists in session

        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password124!', #mismatch passwords
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context['form'] #checking the error thrown by the form
        self.assertIn('password2', form.errors.keys())  # Check if 'password2' is in the errors
        self.assertIn("Passwords entered do not match", form.errors['password2'][0])  # Check for the specific error message

    def test_user_login_regularUser(self):
        print("Method: test_user_login")

        #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        #self.assertEqual(response.status_code, 200)  # Assuming a successful POST request
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)

        
    def test_user_login_provider(self):
        print("Method: test_user_login_provider")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        #user login w provider w wrong password
        url2 = reverse('login')
        data2 = {
            'email': 'test@example.com',
            'password': 'password345!'
        }
        response2 = self.client.post(url2, data2)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Incorrect email or password!')

        #user login w provider w wrong email
        url2 = reverse('login')
        data2 = {
            'email': 'test@hotmail.com',
            'password': 'password123!'
        }
        response2 = self.client.post(url2, data2)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 4)
        self.assertEqual(str(messages2[3]), f'Incorrect email or password!')
    
    def test_logout_regularUser(self):
        print("Method: test_logout_regularUser")

        #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        #self.assertEqual(response.status_code, 200)  # Assuming a successful POST request
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        #logout
        url3 = reverse('logout')
        response3 = self.client.post(url3)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 302)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_user_login_provider(self):
        print("Method: test_user_login_provider")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        #logout
        url3 = reverse('logout')
        response3 = self.client.post(url3)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 302)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_providerUserAlreadyExists(self):
        print("Method: test_providerUserAlreadyExists")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        self.provider2 = Provider.objects.create(
            provider_id='1508823618', #usually ten digits
            firstName='DAVID',
            lastName='GRIFFIN',
            gender='M', #one character in csv file
            phone_number= '8645123076',
            specialization='GYNECOLOGICAL ONCOLOGY',
            address='1 SAINT FRANCIS DR',
            city='ANDERSON',
            state='SC',
            zip_code='296211580',
            facility_name='ANMED HEALTH'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        #creating an account again
        url2 = reverse('create_provider_account')
        data2 = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response2 = self.client.post(url2, data2)
       # self.assertEqual(response.status_code, 302)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'An account with this email already exists. Please log in.')

        #logout
        url3 = reverse('logout')
        response3 = self.client.post(url3)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 302)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)


        #creating an account again
        url4 = reverse('check_provider_id')
        provider_id = {'provider_id': '1508823618'} #valid
        valid_response = self.client.post(url4, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)
        url4 = reverse('create_provider_account')
        data4 = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response4 = self.client.post(url4, data4)
        self.assertEqual(response4.status_code, 200)
        messages4 = list(get_messages(response4.wsgi_request))
        self.assertEqual(len(messages4), 1)
        self.assertEqual(str(messages4[0]), f'User already exists.')

    def test_regularUserExists(self):
        print("Method: test_regularUserExists")

        #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        
        #creating an account again
        url2 = reverse('create_user_account')
        data2 = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'newpassword123!',
            'password2': 'newpassword123!',
        }
        response2 = self.client.post(url2, data2, follow=True)
       # self.assertEqual(response2.status_code, 200)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'An account with this email already exists. Please log in.')

         #logout
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        
        #creating an account again -> with different name 
        url4 = reverse('create_user_account')
        data4 = {
            'email': 'test@example.com',
            'first_name': 'John1',
            'last_name': 'Doe',
            'password': 'newpassword123!',
            'password2': 'newpassword123!',
        }
        response4 = self.client.post(url4, data4)
        self.assertEqual(response4.status_code, 200)
        messages4 = list(get_messages(response4.wsgi_request))
        self.assertEqual(len(messages4),1)
        self.assertEqual(str(messages4[0]), f'User already exists.')

    def test_user_create_account_w_deleted_account(self):
        print("Method: test_user_login_w_deleted_account")

       #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').first().first_name == 'John')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

       #creating an account after deleted
        url2 = reverse('create_user_account')
        data2 = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response3 = self.client.post(url2, data2)
        messages3 = list(get_messages(response3.wsgi_request))
        self.assertEqual(len(messages3), 4)
        self.assertEqual(str(messages3[3]), f'Your account has been deactivated. Please contact us to re-activate it.')
    
    def test_provider_create_account_w_deleted_account(self):
        print("Method: test_provider_login_w_deleted_account")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)


        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').first().first_name == 'TAMMY')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

       #creating an account after deleted
        url = reverse('check_provider_id')
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response3 = self.client.post(url, data)
        messages3 = list(get_messages(response3.wsgi_request))
        self.assertEqual(len(messages3), 1)
        self.assertEqual(str(messages3[0]), f'Your account has been deactivated. Please contact us to re-activate it.')
    
    def test_user_delete_account_w_appt(self):
        print("Method: test_user_delete_account_w_appt")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        
        #logout for provider
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

         #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        # Create an appointment object -> past appointment
        past_start_time = timezone.now() - timezone.timedelta(days=1)
        self.appt = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = past_start_time,
            type = 'new patient',
        )
        self.appt_id = self.appt.pk

        # Create future appointment
        future_start_time = timezone.now() + timezone.timedelta(days=1)
        # Create an appointment object -> future appointment
        self.future_appt = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = future_start_time,
            type = 'follow up',
        )

        self.future_appt_id = self.future_appt.pk

        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').first().first_name == 'John')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

        # Verify only future appointments are canceled
        self.assertTrue(Appointment.objects.filter(pk=self.future_appt_id, canceled=True).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt_id, canceled=True).first().canceled_reason, 'Patient account deactivated/deleted')
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt_id, canceled=True).first().start_time, future_start_time)
        #Verify past appointments are not canceled
        self.assertFalse(Appointment.objects.filter(pk=self.appt_id, canceled=False).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.appt_id, canceled=False).first().start_time, past_start_time)
        
    def test_user_delete_account(self):
        print("Method: test_user_delete_account")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        
        #logout for provider
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

         #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        
        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').first().first_name == 'John')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

    def test_user_delete_account_w_appts(self):
        print("Method: test_user_delete_account_w_appts")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        
        #logout for provider
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

         #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        # Create an appointment object -> past appointment
        past_start_time = timezone.now() - timezone.timedelta(days=1)
        self.appt = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = past_start_time,
            type = 'new patient',
        )
        self.appt_id = self.appt.pk

         # Create an appointment object -> past appointment
        past_start_time2 = timezone.now() - timezone.timedelta(days=2)
        self.appt2 = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = past_start_time2,
            type = 'new patient',
        )
        self.appt2_id = self.appt2.pk

        # Create future appointment
        future_start_time1 = timezone.now() + timezone.timedelta(days=1)
        # Create an appointment object -> future appointment
        self.future_appt1 = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = future_start_time1,
            type = 'follow up',
        )

        self.future_appt1_id = self.future_appt1.pk

        # Create future appointment
        future_start_time2 = timezone.now() + timezone.timedelta(days=2)
        # Create an appointment object -> future appointment
        self.future_appt2 = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = future_start_time2,
            type = 'follow up',
        )

        self.future_appt2_id = self.future_appt2.pk

        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').first().first_name == 'John')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

        # Verify only future appointments are canceled
        self.assertTrue(Appointment.objects.filter(pk=self.future_appt1_id, canceled=True).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt1_id, canceled=True).first().canceled_reason, 'Patient account deactivated/deleted')
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt1_id, canceled=True).first().start_time, future_start_time1)
        self.assertTrue(Appointment.objects.filter(pk=self.future_appt2_id, canceled=True).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt2_id, canceled=True).first().canceled_reason, 'Patient account deactivated/deleted')
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt2_id, canceled=True).first().start_time, future_start_time2)
        #Verify past appointments are not canceled
        self.assertFalse(Appointment.objects.filter(pk=self.appt_id, canceled=False).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.appt_id, canceled=False).first().start_time, past_start_time)
        self.assertFalse(Appointment.objects.filter(pk=self.appt2_id, canceled=False).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.appt2_id, canceled=False).first().start_time, past_start_time2)
    
    def test_user_delete_account(self):
        print("Method: test_user_delete_account")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        
        #logout for provider
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

         #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        
        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').first().first_name == 'John')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

    def test_provider_delete_account_w_appts(self):
        print("Method: test_provider_delete_account_w_appts")

         #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.user.first_name} {profileFound.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        
        #logout for user
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        # Create an appointment object -> past appointment
        past_start_time = timezone.now() - timezone.timedelta(days=1)
        self.appt = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = past_start_time,
            type = 'new patient',
        )
        self.appt_id = self.appt.pk

         # Create an appointment object -> past appointment
        past_start_time2 = timezone.now() - timezone.timedelta(days=2)
        self.appt2 = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = past_start_time2,
            type = 'new patient',
        )
        self.appt2_id = self.appt2.pk

        # Create future appointment
        future_start_time1 = timezone.now() + timezone.timedelta(days=1)
        # Create an appointment object -> future appointment
        self.future_appt1 = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = future_start_time1,
            type = 'follow up',
        )

        self.future_appt1_id = self.future_appt1.pk

        # Create future appointment
        future_start_time2 = timezone.now() + timezone.timedelta(days=2)
        # Create an appointment object -> future appointment
        self.future_appt2 = Appointment.objects.create(
            patient_user = CustomUser.objects.filter(email='test@example.com').first(),
            provider_user = CustomUser.objects.filter(email='test2@example.com').first(),
            start_time = future_start_time2,
            type = 'follow up',
        )

        self.future_appt2_id = self.future_appt2.pk

        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue(CustomUser.objects.filter(email='test2@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test2@example.com').first().first_name == 'TAMMY')
        self.assertFalse(CustomUser.objects.filter(email='test2@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')

        # Verify only future appointments are canceled
        self.assertTrue(Appointment.objects.filter(pk=self.future_appt1_id, canceled=True).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt1_id, canceled=True).first().canceled_reason, 'Provider account deactivated/deleted')
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt1_id, canceled=True).first().start_time, future_start_time1)
        self.assertTrue(Appointment.objects.filter(pk=self.future_appt2_id, canceled=True).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt2_id, canceled=True).first().canceled_reason, 'Provider account deactivated/deleted')
        self.assertEqual(Appointment.objects.filter(pk=self.future_appt2_id, canceled=True).first().start_time, future_start_time2)
        #Verify past appointments are not canceled
        self.assertFalse(Appointment.objects.filter(pk=self.appt_id, canceled=False).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.appt_id, canceled=False).first().start_time, past_start_time)
        self.assertFalse(Appointment.objects.filter(pk=self.appt2_id, canceled=False).first().canceled)
        self.assertEqual(Appointment.objects.filter(pk=self.appt2_id, canceled=False).first().start_time, past_start_time2)
    
    def test_provider_delete_account(self):
        print("Method: test_provider_delete_account")

        #creating provider id
        url = reverse('check_provider_id')
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )
        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        #deleting the account
        url2 = reverse('delete_account')
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue(CustomUser.objects.filter(email='test2@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='test2@example.com').first().first_name == 'TAMMY')
        self.assertFalse(CustomUser.objects.filter(email='test2@example.com').first().is_active)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 3)
        self.assertEqual(str(messages2[2]), f'Account deleted successfully')
    
    def test_provider_list(self):
        print("Method: test_provider_list")
        client = Client()
        response = client.get(reverse('provider_list'))
        self.assertEqual(response.status_code, 200)

    def test_search_provider_name(self):
        print("Method: test_search_provider_name")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'name_query': 'Tammy Jones'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider = response.context['provider_list'][0]
        self.assertEqual(provider.firstName, 'TAMMY')
        self.assertEqual(provider.lastName, 'JONES')

    def test_search_provider_gender(self):
        print("Method: test_search_provider_gender")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'gender': 'F'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Check if the correct provider is returned
        provider = response.context['provider_list'][0]
        self.assertEqual(provider.firstName, 'CARMEN')
        self.assertEqual(provider.lastName, 'JIMENEZ')
        provider2 = response.context['provider_list'][1]
        self.assertEqual(provider2.firstName, 'TAMMY')
        self.assertEqual(provider2.lastName, 'JONES')
    
    def test_search_provider_specialization(self):
        print("Method: test_search_provider_specialization")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'specialization': 'nurse'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider2 = response.context['provider_list'][0]
        self.assertEqual(provider2.firstName, 'TAMMY')
        self.assertEqual(provider2.lastName, 'JONES')

    def test_search_provider_city(self):
        print("Method: test_search_provider_city")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'city': 'Bridgeport'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider2 = response.context['provider_list'][0]
        self.assertEqual(provider2.firstName, 'TAMMY')
        self.assertEqual(provider2.lastName, 'JONES')
    
    def test_search_provider_state(self):
        print("Method: test_search_provider_state")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'state': 'CO'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider2 = response.context['provider_list'][0]
        self.assertEqual(provider2.firstName, 'CARMEN')
        self.assertEqual(provider2.lastName, 'JIMENEZ')
    
    def test_search_provider_zipCode(self):
        print("Method: test_search_provider_zipCode")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'zip_code': '802372'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider2 = response.context['provider_list'][0]
        self.assertEqual(provider2.firstName, 'CARMEN')
        self.assertEqual(provider2.lastName, 'JIMENEZ')

    def test_search_provider_facility(self):
        print("Method: test_search_provider_facility")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 2)

        # Set up request with search parameters
        data = {'facility_name': 'TRUECARE24'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider2 = response.context['provider_list'][0]
        self.assertEqual(provider2.firstName, 'CARMEN')
        self.assertEqual(provider2.lastName, 'JIMENEZ')
    
    def test_search_provider_multiple(self):
        print("Method: test_search_provider_multiple")
        
         # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        # Create a provider
        self.provider2 = Provider.objects.create(
            provider_id='1578840864', #usually ten digits
            firstName='CARMEN',
            lastName='JIMENEZ',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='DENVER',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        # Create a provider
        self.provider3 = Provider.objects.create(
            provider_id='1578840862', #usually ten digits
            firstName='TEST',
            lastName='TEST',
            gender='F', #one character in csv file
            phone_number= '6309521412',
            specialization='CLINICAL SOCIAL WORKER',
            address='7900 E UNION AVE',
            city='BRIDGEPORT',
            state='CO',
            zip_code='802372746',
            facility_name='TRUECARE24 PHYSICIANS GROUP, S.C.'
        )
        url = reverse('provider_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 3)

        # Set up request with search parameters
        data = {'state': 'CO', 'city': 'Denver', 'zip_code': '80237'}  # Searching for 'Tammy Jones'

        # Attach request to the view
        response = self.client.get(url, data)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check if providers are present in the context
        self.assertTrue('provider_list' in response.context)

        # Check if the correct number of providers are present in the context
        self.assertEqual(len(response.context['provider_list']), 1)

        # Check if the correct provider is returned
        provider2 = response.context['provider_list'][0]
        self.assertEqual(provider2.firstName, 'CARMEN')
        self.assertEqual(provider2.lastName, 'JIMENEZ')
        
    def test_user_request_appt(self):
        print("Method: test_user_request_appt")

        url = reverse('check_provider_id')
        # Create a provider
        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        provider_id = {'provider_id': '1114033073'} #valid
        valid_response = self.client.post(url, provider_id, follow=True)
        self.assertEqual(valid_response.status_code, 200)

        #creating provider account
        url = reverse('create_provider_account')
        data = {
            'email': 'test2@example.com',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        profileFound = Profile.objects.get(user__email='test2@example.com', is_doctor=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound.provider.firstName} {profileFound.provider.lastName}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound.user.first_name} {profileFound.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        
        #logout for provider
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        # Check that the response status code is 302 (redirect)
        self.assertEqual(response3.status_code, 200)
        # Check that the user is redirected to the login page after logout
        self.assertRedirects(response3, reverse('login'))
        # Check that the user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

         #creating an account st its data is saved in CustomUser
        url = reverse('create_user_account')
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123!',
            'password2': 'password123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming a successful POST request - redirect
       # self.assertRedirects(response, reverse('profile'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='test@example.com').first_name, 'John') #checking if customuser has attributes
        self.assertEqual(CustomUser.objects.get(email='test@example.com').last_name, 'Doe')
        self.assertTrue(Profile.objects.filter(user__email='test@example.com', is_doctor=False).exists())
        profileFound2 = Profile.objects.get(user__email='test@example.com', is_doctor=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), f'Your Account has been created {profileFound2.user.first_name} {profileFound2.user.last_name}!')
        self.assertEqual(str(messages[1]), f'Welcome {profileFound2.user.first_name} {profileFound2.user.last_name}!')
        # Check that the user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment

            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': profileFound2.user.first_name,
                'patient_lastName': profileFound2.user.last_name,
                'email': profileFound2.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': profileFound.provider.firstName,
                'provider_lastName': profileFound.provider.lastName,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(provider_user = profileFound.user, start_time__date=appointment_date).exists())
            appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='test@example.com'), provider_user=CustomUser.objects.get(email='test2@example.com'))
            self.assertEqual(appointment.start_time.date(), appointment_date.date())
            self.assertEqual(appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 3)
            self.assertEqual(str(messages[2]), f'Appointment requested successfully')
            # check if adding an appointment with the same date and time is not possible
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            data = {
                'patient_firstName': profileFound2.user.first_name,
                'patient_lastName': profileFound2.user.last_name,
                'email': profileFound2.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': profileFound.provider.firstName,
                'provider_lastName': profileFound.provider.lastName,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'The appointment slot is not available.')

            # check if adding an appointment with past date is not possible
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() - timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': profileFound2.user.first_name,
                'patient_lastName': profileFound2.user.last_name,
                'email': profileFound2.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': profileFound.provider.firstName,
                'provider_lastName': profileFound.provider.lastName,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertFalse(Appointment.objects.filter(provider_user = profileFound.user, start_time__date=appointment_date).exists())
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'You can only schedule appointments for future dates.')

            # checkig if adding another appointment with different date and time is possible
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=2) # for tomorrow
            data = {
                'patient_firstName': profileFound2.user.first_name,
                'patient_lastName': profileFound2.user.last_name,
                'email': profileFound2.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': profileFound.provider.firstName,
                'provider_lastName': profileFound.provider.lastName,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(provider_user = profileFound.user, start_time__date=appointment_date).exists())
            appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='test@example.com'), provider_user=CustomUser.objects.get(email='test2@example.com'), start_time__date=appointment_date)
            self.assertEqual(appointment.start_time.date(), appointment_date.date())
            self.assertEqual(appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')

    def test_provider_request_appt_check(self):
        print("Method: test_provider_request_appt_check")

        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(patient_user = self.user_profile.user, start_time__date=appointment_date).exists())
            appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='patient@example.com'), provider_user=CustomUser.objects.get(email='provider@example.com'))
            self.assertEqual(appointment.start_time.date(), appointment_date.date())
            self.assertEqual(appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')

            #logout for patient
            url3 = reverse('logout')
            response3 = self.client.post(url3, follow=True)
            self.assertEqual(response3.status_code, 200)
            # Check that the user is redirected to the login page after logout
            self.assertRedirects(response3, reverse('login'))
            # Check that the user is logged out
            self.assertFalse('_auth_user_id' in self.client.session)

            url2 = reverse('login')
            data2 = {
                'email': 'provider@example.com',
                'password': 'testpassword'
            }
            response2 = self.client.post(url2, data2, follow=True)
            self.assertEqual(response2.status_code, 200) 
            messages = list(get_messages(response2.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Welcome {self.provider.firstName} {self.provider.lastName}!')
            self.assertTrue('_auth_user_id' in self.client.session)

            # check if the provider can see the appointment request in messages
            url = reverse('messages')
            response = self.client.get(url, follow=True)    
            self.assertEqual(response.status_code, 200)
            self.assertTrue('messages' in response.context)
            self.assertEqual(Message.objects.filter(sender=self.patient_user, recipient=self.provider_user).first().subject, 'Appointment Request')

            # check if the provider can see the appointment request in appointments
            url = reverse('appointments')
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(Appointment.objects.filter(patient_user=self.patient_user).exists())
            self.assertEqual(Appointment.objects.filter(patient_user=self.patient_user).first().status, 'pending')

    def test_provider_approve_appt(self):
        print("Method: test_provider_approve_appt")

        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(patient_user = self.user_profile.user, start_time__date=appointment_date).exists())
            self.appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='patient@example.com'), provider_user=CustomUser.objects.get(email='provider@example.com'))
            self.assertEqual(self.appointment.start_time.date(), appointment_date.date())
            self.assertEqual(self.appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')

            #logout for patient
            url3 = reverse('logout')
            response3 = self.client.post(url3, follow=True)
            self.assertEqual(response3.status_code, 200)
            # Check that the user is redirected to the login page after logout
            self.assertRedirects(response3, reverse('login'))
            # Check that the user is logged out
            self.assertFalse('_auth_user_id' in self.client.session)

            url2 = reverse('login')
            data2 = {
                'email': 'provider@example.com',
                'password': 'testpassword'
            }
            response2 = self.client.post(url2, data2, follow=True)
            self.assertEqual(response2.status_code, 200) 
            messages = list(get_messages(response2.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Welcome {self.provider.firstName} {self.provider.lastName}!')
            self.assertTrue('_auth_user_id' in self.client.session)


            # approve the appointment
            self.assertEqual(self.appointment.status, 'pending')
            url = reverse('appointment-details', kwargs={'pk': self.appointment.pk})
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, 200)
            #mocking the javascript function
            ajax_payload = {'status': 'approved', 'csrfmiddlewaretoken': 'dummy_csrf_token'}
            ajax_response = self.client.post(url + '/appointment_status', ajax_payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(ajax_response.status_code, 200)
            self.assertEqual(ajax_response.json()['success'], True)
            appointment = Appointment.objects.get(pk=self.appointment.pk)
            appointment.refresh_from_db() #refresh the object from the database
            self.assertEqual(appointment.status, 'approved')

            #logout for provider
            url3 = reverse('logout')
            response3 = self.client.post(url3, follow=True)
            self.assertEqual(response3.status_code, 200)
            # Check that the user is redirected to the login page after logout
            self.assertRedirects(response3, reverse('login'))
            # Check that the user is logged out
            self.assertFalse('_auth_user_id' in self.client.session)

            url2 = reverse('login')
            data2 = {
                'email': 'patient@example.com',
                'password': 'testpassword'
            }
            response2 = self.client.post(url2, data2, follow=True)
            self.assertEqual(response2.status_code, 200) 
            messages = list(get_messages(response2.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
            self.assertTrue('_auth_user_id' in self.client.session)

            url = reverse('messages')
            response = self.client.get(url, follow=True)    
            self.assertEqual(response.status_code, 200)
            self.assertTrue('messages' in response.context)
            self.assertEqual(Message.objects.filter(sender=self.provider_user, recipient=self.patient_user).first().subject, 'Appointment Approved')

    def test_provider_reject_appt(self):
        print("Method: test_provider_reject_appt")
        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(patient_user = self.user_profile.user, start_time__date=appointment_date).exists())
            self.appointment2 = Appointment.objects.get(patient_user=CustomUser.objects.get(email='patient@example.com'), provider_user=CustomUser.objects.get(email='provider@example.com'))
            self.assertEqual(self.appointment2.start_time.date(), appointment_date.date())
            self.assertEqual(self.appointment2.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')

            #logout for patient
            url3 = reverse('logout')
            response3 = self.client.post(url3, follow=True)
            self.assertEqual(response3.status_code, 200)
            # Check that the user is redirected to the login page after logout
            self.assertRedirects(response3, reverse('login'))
            # Check that the user is logged out
            self.assertFalse('_auth_user_id' in self.client.session)

            url2 = reverse('login')
            data2 = {
                'email': 'provider@example.com',
                'password': 'testpassword'
            }
            response2 = self.client.post(url2, data2, follow=True)
            self.assertEqual(response2.status_code, 200) 
            messages = list(get_messages(response2.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Welcome {self.provider.firstName} {self.provider.lastName}!')
            self.assertTrue('_auth_user_id' in self.client.session)


            # reject the appointment
            self.assertEqual(self.appointment2.status, 'pending')
            url = reverse('appointment-details', kwargs={'pk': self.appointment2.pk})
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, 200)
            #mocking the javascript function
            ajax_payload = {'status': 'rejected', 'csrfmiddlewaretoken': 'dummy_csrf_token'}
            ajax_response = self.client.post(url + '/appointment_status', ajax_payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(ajax_response.status_code, 200)
            self.assertEqual(ajax_response.json()['success'], True)
            appointment = Appointment.objects.get(pk=self.appointment2.pk)
            appointment.refresh_from_db() #refresh the object from the database
            self.assertEqual(appointment.status, 'rejected')

            #logout for provider
            url3 = reverse('logout')
            response3 = self.client.post(url3, follow=True)
            self.assertEqual(response3.status_code, 200)
            # Check that the user is redirected to the login page after logout
            self.assertRedirects(response3, reverse('login'))
            # Check that the user is logged out
            self.assertFalse('_auth_user_id' in self.client.session)

            url2 = reverse('login')
            data2 = {
                'email': 'patient@example.com',
                'password': 'testpassword'
            }
            response2 = self.client.post(url2, data2, follow=True)
            self.assertEqual(response2.status_code, 200) 
            messages = list(get_messages(response2.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
            self.assertTrue('_auth_user_id' in self.client.session)

            url = reverse('messages')
            response = self.client.get(url, follow=True)    
            self.assertEqual(response.status_code, 200)
            self.assertTrue('messages' in response.context)
            self.assertEqual(Message.objects.filter(sender=self.provider_user, recipient=self.patient_user).first().subject, 'Appointment Rejected')

    def test_reply_message(self):
        print("Method: test_reply_message")
        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)

        # send a message
        url = reverse('send_message', kwargs={'id': self.provider.pk})
        data = {
            'sender': self.patient_user.pk, 
            'recipient': self.provider_user.pk,
            'subject': 'Test Subject',
            'content': 'Test Message'
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Message.objects.filter(sender=self.patient_user, recipient=self.provider_user).exists())
        self.message = Message.objects.get(sender=self.patient_user, recipient=self.provider_user)
        self.assertEqual(self.message.subject, 'Test Subject')
        self.assertEqual(self.message.content, 'Test Message')

        #logout for patient
        url3 = reverse('logout')
        response3 = self.client.post(url3, follow=True)
        self.assertEqual(response3.status_code, 200)
        
        
        # login as provider
        url2 = reverse('login')
        data2 = {
            'email': 'provider@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.provider.firstName} {self.provider.lastName}!')
        self.assertTrue('_auth_user_id' in self.client.session)

        # check if the provider can reply to the message
        url = reverse('messages')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('messages' in response.context)
        self.assertEqual(Message.objects.filter(sender=self.patient_user, recipient=self.provider_user).first().subject, 'Test Subject')
    
        url = reverse('reply_message', kwargs={'id': self.message.pk})
        data = {
            'sender': self.provider_user.pk, 
            'recipient': self.patient_user.pk,
            'subject': 'Re: Test Subject',
            'content': 'Test Reply'
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Message.objects.filter(sender=self.provider_user, recipient=self.patient_user).exists())
        self.message2 = Message.objects.get(sender=self.provider_user, recipient=self.patient_user)
        self.assertEqual(self.message2.content, 'Test Reply')
        
    def test_user_cancel_appt(self):
        print("Method: user_cancel_appt")

        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(patient_user = self.user_profile.user, start_time__date=appointment_date).exists())
            self.appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='patient@example.com'), provider_user=CustomUser.objects.get(email='provider@example.com'))
            self.assertEqual(self.appointment.start_time.date(), appointment_date.date())
            self.assertEqual(self.appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')

        url = reverse('appointment-details', kwargs={'pk': self.appointment.pk})
        response = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        #mocking the javascript function
        ajax_payload = {'csrfmiddlewaretoken': 'dummy_csrf_token'}
        ajax_response = self.client.post(url + '/cancel_appointment', ajax_payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(ajax_response.status_code, 200)
        self.assertEqual(ajax_response.json()['success'], True)

        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.canceled)

    
    def test_user_cancel_appt_reschedule(self):
        print("Method: user_cancel_appt_reschedule")

        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(patient_user = self.user_profile.user, start_time__date=appointment_date).exists())
            self.appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='patient@example.com'), provider_user=CustomUser.objects.get(email='provider@example.com'))
            self.assertEqual(self.appointment.start_time.date(), appointment_date.date())
            self.assertEqual(self.appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')
        
        #checking you can't schedule an appointment on the same day and time
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'The appointment slot is not available.')


        url = reverse('appointment-details', kwargs={'pk': self.appointment.pk})
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        #mocking the javascript function
        ajax_payload = {'csrfmiddlewaretoken': 'dummy_csrf_token'}
        ajax_response = self.client.post(url + '/cancel_appointment', ajax_payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(ajax_response.status_code, 200)
        self.assertEqual(ajax_response.json()['success'], True)

        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.canceled)

        # reschedule the appointment on same day and time
        with warnings.catch_warnings(): # to ignore the time zone support is active warning
            warnings.simplefilter("ignore")
            # request an appointment
            url = reverse('request_appointment', kwargs={'id': self.provider.pk})
            appointment_date = timezone.now() + timedelta(days=1) # for tomorrow
            data = {
                'patient_firstName': self.user_profile.user.first_name,
                'patient_lastName': self.user_profile.user.last_name,
                'email': self.user_profile.user.email,
                'type': 'new patient',
                'appointment_date': appointment_date.date(),
                'appointment_time': appointment_date.time(),
                'provider_firstName': self.provider_profile.user.first_name,
                'provider_lastName': self.provider_profile.user.last_name,
                'services_info': 'Service information'
            }
            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 200) 
            self.assertTrue(Appointment.objects.filter(patient_user = self.user_profile.user, start_time__date=appointment_date).exists())
            self.appointment = Appointment.objects.get(patient_user=CustomUser.objects.get(email='patient@example.com'), provider_user=CustomUser.objects.get(email='provider@example.com'), canceled=False)
            self.assertEqual(self.appointment.start_time.date(), appointment_date.date())
            self.assertEqual(self.appointment.status, 'pending')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), f'Appointment requested successfully')

    def test_user_cancel_appt_past_appt(self):
        print("Method: user_cancel_appt_past_appt")

        # Create a custom user that will be our patient
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

         # Create a provider who will be our provider
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

        self.provider = Provider.objects.create(
            provider_id='1114033073', #usually ten digits
            firstName='TAMMY',
            lastName='JONES',
            gender='F', #one character in csv file
            phone_number= '6813423153',
            specialization='CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)',
            address='327 MEDICAL PARK DR',
            city='BRIDGEPORT',
            state='WV',
            zip_code='263309006',
            facility_name='UNITED HOSPITAL CENTER INC'
        )

        self.provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider)

        # Create an appointment that is in the past
        self.appt = Appointment.objects.create(
            patient_user = self.patient_user,
            provider_user = self.provider_user,
            start_time = timezone.now() - timedelta(days=1), # for yesterday
            type = 'new patient',
            status = 'approved',
        )

        self.appt_id = self.appt.pk

        # login as patient
        url2 = reverse('login')
        data2 = {
            'email': 'patient@example.com',
            'password': 'testpassword'
        }
        response2 = self.client.post(url2, data2, follow=True)
        self.assertEqual(response2.status_code, 200) 
        messages = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Welcome {self.patient_user.first_name} {self.patient_user.last_name}!')
        self.assertTrue('_auth_user_id' in self.client.session)

        #with patch('your_app.views.cancel_appt') as mock_cancel_appt:

        url = reverse('appointment-details', kwargs={'pk': self.appt_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        #mocking the javascript function
        ajax_payload = {'csrfmiddlewaretoken': 'dummy_csrf_token'}
        ajax_response = self.client.post(url + '/cancel_appointment', ajax_payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(ajax_response.status_code, 200)
        self.assertEqual(ajax_response.json()['success'], False)
        self.assertEqual(ajax_response.json()['error_message'], 'past_appointment')
         

        self.appt.refresh_from_db()
        self.assertFalse(self.appt.canceled)


