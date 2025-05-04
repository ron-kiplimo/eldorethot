from django import forms
from .models import Escort

class EscortForm(forms.ModelForm):
    class Meta:
        model = Escort
        fields = ['name', 'age', 'city', 'services', 'rates', 'availability', 'profile_image', 'bio', 'phone_number']
        widgets = {
            'services': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 5}),
        }