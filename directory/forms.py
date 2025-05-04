from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Escort

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EscortForm(forms.ModelForm):
    class Meta:
        model = Escort
        fields = ['name', 'age', 'city', 'services', 'rates', 'availability', 'profile_image', 'bio', 'phone_number']