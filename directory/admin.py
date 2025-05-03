
# Register your models here.
from django.contrib import admin
from .models import Escort

@admin.register(Escort)
class EscortAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'city', 'rates']
    search_fields = ['name', 'city', 'services']

