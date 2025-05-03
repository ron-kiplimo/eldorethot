from django import forms
from .models import Escort
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class EscortForm(forms.ModelForm):
    class Meta:
        model = Escort
        exclude = ['user', 'created_at']

from django import forms
from .models import Escort

class EscortForm(forms.ModelForm):
    class Meta:
        model = Escort
        fields = ['name', 'city', 'age', 'rates', 'profile_image']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']