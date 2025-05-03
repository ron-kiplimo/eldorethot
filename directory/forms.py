from django import forms
from .models import Escort

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
