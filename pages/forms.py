from django import forms
from .models import CustomUser, Provider, Feedback, Message, Appointment
from django.contrib.auth import password_validation
from django.forms import Select
import django.forms.widgets
from django.utils import timezone
from datetime import timedelta

STATES = {
    '': '', 'AL': 'AL', 'AK': 'AK', 'AZ': 'AZ', 'AR': 'AR', 'CA': 'CA', 'CO': 'CO',
    'CT': 'CT', 'DE': 'DE', 'FL': 'FL', 'GA': 'GA', 'HI': 'HI', 'ID': 'ID',
    'IL': 'IL', 'IN': 'IN', 'IA': 'IA', 'KS': 'KS', 'KY': 'KY', 'LA': 'LA',
    'ME': 'ME', 'MD': 'MD', 'MA': 'MA', 'MI': 'MI', 'MN': 'MN', 'MS': 'MS',
    'MO': 'MO', 'MT': 'MT', 'NE': 'NE', 'NV': 'NV', 'NH': 'NH', 'NJ': 'NJ',
    'NM': 'NM', 'NY': 'NY', 'NC': 'NC', 'ND': 'ND', 'OH': 'OH', 'OK': 'OK',
    'OR': 'OR', 'PA': 'PA', 'RI': 'RI', 'SC': 'SC', 'SD': 'SD', 'TN': 'TN',
    'TX': 'TX', 'UT': 'UT', 'VT': 'VT', 'VA': 'VA', 'WA': 'WA', 'WV': 'WV',
    'WI': 'WI', 'WY': 'WY',
}


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput,
                               help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']


class ProviderRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput,
                               help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class ProviderIdForm(forms.Form):
    provider_id = forms.CharField(max_length=10)


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class ProviderUpdateForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ["provider_id", "firstName", "lastName", "gender", "phone_number", "specialization", "address", "city",
                  "state", "zip_code", "facility_name"]


class SendMessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(queryset=CustomUser.objects.all(), widget=forms.HiddenInput())
    sender = forms.ModelChoiceField(queryset=CustomUser.objects.all(), widget=forms.HiddenInput())
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-input mx-auto block w-3/4 md:w-1/2 border-gray-300 rounded-md shadow-sm"
        })
    )
    content = forms.CharField(widget=forms.Textarea(attrs={
        "class": "textarea mx-auto block w-3/4 md:w-1/2 border-2 border-blue-500 rounded-md shadow-sm",
        "rows": 4
    }))
    class Meta:
        model = Message
        fields = ['recipient', 'sender', 'subject', 'content']


class UserUpdateForm(forms.ModelForm):
    ## Look at UserRegistrationForm and pick specific fields
    date_joined = forms.CharField(widget=forms.DateTimeInput(attrs={'class': 'disabled', 'readonly': 'readonly'}))
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'indented'}))
    first_name = forms.CharField(required=True, disabled=True)
    last_name = forms.CharField(required=True, disabled=True)

    class Meta:
        model = CustomUser
        fields = ['date_joined', 'email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True
        self.fields['date_joined'].widget.attrs['readonly'] = True


class ProviderSearchForm(forms.Form):
    name_query = forms.CharField(label='Name', required=False)
    gender = forms.ChoiceField(label='Gender', choices=[('', 'Any'), ('M', 'Male'), ('F', 'Female')], required=False)
    specialization = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.ChoiceField(choices=sorted(STATES.items(), key=lambda x: x[1]), required=False)
    zip_code = forms.CharField(required=False)
    facility_name = forms.CharField(required=False)
    keywords = forms.CharField(required=False)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AppointmentAvailabilityForm(forms.Form):
    patient_firstName = forms.CharField(required=True)
    patient_lastName = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    type = forms.ChoiceField(
        choices=[('new patient', 'new patient'), ('follow up', 'follow up'), ('new condition', 'new condition')],
        required=True)
    appointment_date = forms.DateField(required=True,
                                       widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    appointment_time = forms.TimeField(required=True, widget=forms.TimeInput(attrs={'type': 'time'}))
    provider_firstName = forms.CharField(required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    provider_lastName = forms.CharField(required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    services_info = forms.CharField(required=False)


class SpecialistSuggesterForm(forms.Form):
    OPTIONS = (
        ('abdominal pain', 'abdominal pain'),
        ('abnormal menstruation', 'abnormal menstruation'),
        ('acute liver failure', 'acute liver failure'),
        ('altered sensorium', 'altered sensorium'),
        ('anxiety', 'anxiety'),
        ('back pain', 'back pain'),
        ('belly pain', 'belly pain'),
        ('blackheads', 'blackheads'),
        ('bladder discomfort', 'bladder discomfort'),
        ('blister', 'blister'),
        ('blood in sputum', 'blood in sputum'),
        ('bloody stool', 'bloody stool'),
        ('blurred and distorted vision', 'blurred and distorted vision'),
        ('breathlessness', 'breathlessness'),
        ('brittle nails', 'brittle nails'),
        ('bruising', 'bruising'),
        ('chest pain', 'chest pain'),
        ('chills', 'chills'),
        ('cold hands and feets', 'cold hands and feets'),
        ('coma', 'coma'),
        ('congestion', 'congestion'),
        ('constipation', 'constipation'),
        ('continuous sneezing', 'continuous sneezing'),
        ('cough', 'cough'),
        ('cramps', 'cramps'),
        ('dark urine', 'dark urine'),
        ('dehydration', 'dehydration'),
        ('depression', 'depression'),
        ('diarrhea', 'diarrhea'),
        ('distention of abdomen', 'distention of abdomen'),
        ('dizziness', 'dizziness'),
        ('enlarged thyroid', 'enlarged thyroid'),
        ('excessive hunger', 'excessive hunger'),
        ('fast heart rate', 'fast heart rate'),
        ('fatigue', 'fatigue'),
        ('foul smell of urine', 'foul smell of urine'),
        ('headache', 'headache'),
        ('high fever', 'high fever'),
        ('hip joint pain', 'hip joint pain'),
        ('increased appetite', 'increased appetite'),
        ('indigestion', 'indigestion'),
        ('irregular sugar level', 'irregular sugar level'),
        ('irritability', 'irritability'),
        ('itching', 'itching'),
        ('joint pain', 'joint pain'),
        ('knee pain', 'knee pain'),
        ('lack of concentration', 'lack of concentration'),
        ('lethargy', 'lethargy'),
        ('loss of appetite', 'loss of appetite'),
        ('loss of balance', 'loss of balance'),
        ('loss of smell', 'loss of smell'),
        ('malaise', 'malaise'),
        ('mild fever', 'mild fever'),
        ('mood swings', 'mood swings'),
        ('movement stiffness', 'movement stiffness'),
        ('muscle pain', 'muscle pain'),
        ('muscle wasting', 'muscle wasting'),
        ('muscle weakness', 'muscle weakness'),
        ('nausea', 'nausea'),
        ('neck pain', 'neck pain'),
        ('nodal skin eruptions', 'nodal skin eruptions'),
        ('obesity', 'obesity'),
        ('pain behind the eyes', 'pain behind the eyes'),
        ('pain during bowel movements', 'pain during bowel movements'),
        ('painful walking', 'painful walking'),
        ('palpitations', 'palpitations'),
        ('passage of gases', 'passage of gases'),
        ('patches in throat', 'patches in throat'),
        ('phlegm', 'phlegm'),
        ('polyuria', 'polyuria'),
        ('prominent veins on calf', 'prominent veins on calf'),
        ('puffy face and eyes', 'puffy face and eyes'),
        ('red sore around nose', 'red sore around nose'),
        ('red spots over body', 'red spots over body'),
        ('redness of eyes', 'redness of eyes'),
        ('restlessness', 'restlessness'),
        ('runny nose', 'runny nose'),
        ('shivering', 'shivering'),
        ('sinus pressure', 'sinus pressure'),
        ('skin peeling', 'skin peeling'),
        ('skin rash', 'skin rash'),
        ('slurred speech', 'slurred speech'),
        ('stiff neck', 'stiff neck'),
        ('stomach pain', 'stomach pain'),
        ('sunken eyes', 'sunken eyes'),
        ('sweating', 'sweating'),
        ('swelled lymph nodes', 'swelled lymph nodes'),
        ('swelling joints', 'swelling joints'),
        ('swelling of stomach', 'swelling of stomach'),
        ('swollen extremeties', 'swollen extremeties'),
        ('swollen legs', 'swollen legs'),
        ('throat irritation', 'throat irritation'),
        ('ulcers on tongue', 'ulcers on tongue'),
        ('unsteadiness', 'unsteadiness'),
        ('visual disturbances', 'visual disturbances'),
        ('vomiting', 'vomiting'),
        ('watering from eyes', 'watering from eyes'),
        ('weakness in limbs', 'weakness in limbs'),
        ('weakness of one body side', 'weakness of one body side'),
        ('weight gain', 'weight gain'),
        ('weight loss', 'weight loss'),
        ('yellowing of eyes', 'yellowing of eyes'),
        ('yellowish skin', 'yellowish skin'))
    symptoms = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=OPTIONS)

class ContactUsForm(forms.Form):
   name = forms.CharField(required=True, widget=forms.TextInput())
   email = forms.EmailField(required=True)
   message = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"5"}))

