from django.utils import timezone
from django.test import TestCase
from ..models import CustomUser, Provider, Profile, Message, Feedback, Appointment

# Create your tests here.


class ProviderTest(TestCase):
    def setUp(self):
        print("setUp: Run every time a test is ran.")

        # Create a custom user -> ideally would be assigned to a provider hence not needing first/lastName
        self.user = CustomUser.objects.create_user(
            email='user@example.com', 
            password='testpassword')
        
        # we can set validations on the requirements of first and last name in frontend
        self.regular_user = CustomUser.objects.create_user(
            email='userReg@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')

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

        self.provider3 = Provider.objects.create(
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

        # Create a profile for the provider1
        self.provider_profile = Profile.objects.create(user=self.user, is_doctor=True, provider=self.provider)

        #Create a profile for the regular user
        self.regular_user_profile = Profile.objects.create(user=self.regular_user, is_doctor=False)

    def test_custom_provider_user(self):
        print("Method: test_custom_provider_user.")
        user = CustomUser.objects.get(email='user@example.com')
        self.assertEqual(user.email, 'user@example.com')

    def test_custom_regular_user(self):
        print("Method: test_custom_regular_user.")
        user = CustomUser.objects.get(email='userReg@example.com') #checking if user is created
        self.assertEqual(user.email, 'userReg@example.com')

    def test_provider(self):
        print("Method: test_provider.")
        provider = Provider.objects.get(provider_id='1114033073')
        self.assertEqual(provider.firstName, 'TAMMY')
        self.assertEqual(provider.specialization, 'CERTIFIED REGISTERED NURSE ANESTHETIST (CRNA)')
        provider_no_profile = Provider.objects.get(provider_id='1578840864')
        self.assertEqual(provider_no_profile.firstName, 'CARMEN')
        self.assertEqual(provider_no_profile.specialization, 'CLINICAL SOCIAL WORKER')
        # self.assertEqual(provider.__str__(), f"TAMMY JONES") -> works
    
    def test_claim_profile(self):
        print("Method: test_claim_profile.")
        provider_no_profile = Provider.objects.get(provider_id='1578840864') #grabbing id that already exists for provider
        self.assertEqual(provider_no_profile.firstName, 'CARMEN') #checking if data matches to what already pre exists
        self.assertEqual(provider_no_profile.specialization, 'CLINICAL SOCIAL WORKER')
        user_new = CustomUser.objects.create_user(email='user2@example.com', password='testpassword2') #mimic "creates account" w/o name since account is claimed
        self.provider_profile2 = Profile.objects.create(user=user_new, is_doctor=True, provider=provider_no_profile) #setting to provider claimed profile 
        profile = Profile.objects.get(user=user_new) #get the new provider user from Profile objects
        self.assertEqual(profile.is_doctor, True) #checking if provider
        self.assertEqual(profile.provider, provider_no_profile) #checking the foreign key link data matches
        #testing out save feature to see if can get first/last name from profile w/o assigning it to user
        self.assertEqual(profile.user.first_name, "CARMEN") 
        self.assertEqual(profile.user.last_name, "JIMENEZ")

    def test_provider_profile(self):
        print("Method: test_provider_profile.")
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.is_doctor, True)
        self.assertEqual(profile.provider, self.provider)
        self.assertEqual(profile.provider.firstName, "TAMMY")

    def test_regular_user_profile(self):
        print("Method: test_regular_user_profile.")
        regular_user_profile = Profile.objects.get(user=self.regular_user)
        self.assertEqual(regular_user_profile.is_doctor, False)
        self.assertIsNone(regular_user_profile.provider)
        self.assertEqual(regular_user_profile.user.first_name, "JOE")
        self.assertEqual(regular_user_profile.user.last_name, "DOE")

    def test_get_providers_by_gender(self):
        print("Method: test_get_provider_by_gender.")
        female_providers = Provider.objects.filter(gender='F')
        self.assertEqual(female_providers.count(), 2) 

    def test_get_providers_by_gender(self):
        print("Method: test_get_provider_by_gender.")
        female_providers = Provider.objects.filter(gender='F')
        self.assertEqual(female_providers.count(), 2) 
        male_providers = Provider.objects.filter(gender='M')
        self.assertEqual(male_providers.count(), 1) 

class ProfileTest(TestCase):
    def setUp(self):
        print("Set up profile fixtures...")

         # we can set validations on the requirements of first and last name in frontend
        self.regular_user = CustomUser.objects.create_user(
            email='userReg@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.provider_user = CustomUser.objects.create_user(
            email='provider@example.com', 
            password='testpassword')

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

    def test_get_profile(self):
        print("Method: test_get_profile.")
        #Create a profile for the regular user
        regular_user_profile = Profile.objects.create(user=self.regular_user, is_doctor=False, info='Test info')
        self.assertEqual(regular_user_profile.is_doctor, False)
        self.assertEqual(regular_user_profile.info, 'Test info')
        self.assertEqual(regular_user_profile.user.first_name, 'JOE')
        self.assertEqual(regular_user_profile.user.last_name, 'DOE')

        provider_profile = Profile.objects.create(user=self.provider_user, is_doctor=True, provider=self.provider, info='Test info2')
        self.assertEqual(provider_profile.is_doctor, True)
        self.assertEqual(provider_profile.info, 'Test info2')
        self.assertEqual(provider_profile.user.first_name, 'TAMMY')
        self.assertEqual(provider_profile.user.last_name, 'JONES')



class MessageTest(TestCase):
     def setUp(self):
        print("Set up message fixtures...")

        # Create a custom user that will be our sender
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

        # Create a provider who will be our recipient
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

        # Create a message
        self.message = Message.objects.create(
            sender=self.patient_user,
            recipient=self.provider_user,
            subject='Test message subject',
            content='Text message content',
            is_read=False,
        )

        self.message_id = self.message.pk
   
     def test_get_message(self):
        print("Method: test_get_message: " + str(self.message_id))
        message = Message.objects.get(pk=self.message_id)
        now = timezone.now()
        self.assertEqual(message.subject, "Test message subject")
        self.assertTrue(message.created_at.day == now.day)
        self.assertEqual(message.content, 'Text message content')
        self.assertEqual(message.sender.email, 'patient@example.com')
        self.assertEqual(message.recipient.email, 'provider@example.com')
        self.assertEqual(message.is_read, False)

class FeedbackTest(TestCase):
     def setUp(self):
        print("Set up feedback fixtures...")

        # Create a custom user that will be our sender
        self.patient_user = CustomUser.objects.create_user(
            email='patient@example.com', 
            first_name= 'JOE',
            last_name = 'DOE',
            password='testpassword')
        
        self.user_profile = Profile.objects.create(user=self.patient_user, is_doctor=False)

        # Create a provider who will be our feedback subject
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

        # Create a feedback object
        self.feedback = Feedback.objects.create(
            patient_user=self.patient_user,
            provider=self.provider,
            content='Feedback content'
        )

        self.feedback_id = self.feedback.pk
   
     def test_get_feedback(self):
        print("Method: test_get_feedback: " + str(self.feedback_id))
        feedback = Feedback.objects.get(pk=self.feedback_id)
        now = timezone.now()
        self.assertEqual(feedback.content, "Feedback content")
        self.assertTrue(feedback.created_at.day == now.day)
        self.assertEqual(feedback.patient_user.email, 'patient@example.com')
        self.assertEqual(feedback.provider.provider_id, '1114033073')

class AppointmentTest(TestCase):
     def setUp(self):
        print("Set up appointment fixtures...")

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

        # Create an appointment object
        self.appt = Appointment.objects.create(
            patient_user = self.patient_user,
            provider_user = self.provider_user,
            start_time = timezone.now(),
            type = 'new patient',
        )

        self.appt_id = self.appt.pk
        
        # Create a canceled appointment object
        self.canceled_appt = Appointment.objects.create(
            patient_user = self.patient_user,
            provider_user = self.provider_user,
            start_time = timezone.now(),
            type = 'follow up',
            canceled = True,
            canceled_reason = 'Test reason'
        )

        self.canceled_appt_id = self.canceled_appt.pk
   
     def test_get_appt(self):
        print("Method: test_get_appt: " + str(self.appt_id))
        appointment = Appointment.objects.get(pk=self.appt_id)
        minutes = (appointment.end_time - appointment.start_time).total_seconds() / 60.0
        self.assertEqual(appointment.patient_user.first_name, "JOE")
        self.assertEqual(appointment.provider_user.email, "provider@example.com")
        self.assertEqual(minutes, 60)
        self.assertFalse(appointment.canceled)
        
     def test_get_canceled_appt(self):
        print("Method: test_get_canceled_appt: " + str(self.canceled_appt_id))
        can_appointment = Appointment.objects.get(pk=self.canceled_appt_id)
        can_minutes = (can_appointment.end_time - can_appointment.start_time).total_seconds() / 60.0
        self.assertEqual(can_appointment.patient_user.first_name, "JOE")
        self.assertEqual(can_appointment.provider_user.email, "provider@example.com")
        self.assertEqual(can_minutes, 15)
        self.assertTrue(can_appointment.canceled)
        self.assertEqual(can_appointment.canceled_reason, 'Test reason')

     def test_set_appointment_status(self):
        print("Method: test_set_appointment_status.")
        appointment = Appointment.objects.get(pk=self.appt_id)
        self.assertFalse(appointment.canceled)
        appointment.status = 'approved'
        appointment.save()
        self.assertTrue(appointment.status, 'approved')
        appointment.status = 'rejected'
        appointment.save()
        self.assertTrue(appointment.status, 'rejected')
        appointment.status = 'pending'
        appointment.save()
        self.assertTrue(appointment.status, 'pending')
        

