# eldorethot/views.py
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("🏰 Welcome to Eldorethot!")



# Define the escort_dashboard view
def escort_dashboard(request):
    return render(request, 'escort_dashboard.html')  # You can add context here if needed
