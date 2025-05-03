from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Escort, Rating

class EscortForm(forms.ModelForm):
    class Meta:
        model = Escort
        fields = ['name', 'age', 'city', 'services', 'rates', 'availability', 'profile_image', 'bio']

def escort_list(request):
    query = request.GET.get('q')
    if query:
        escorts = Escort.objects.filter(name__icontains=query) | Escort.objects.filter(city__icontains=query)
    else:
        escorts = Escort.objects.all()
    paginator = Paginator(escorts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'directory/escort_list.html', {'page_obj': page_obj})

@login_required
def escort_detail(request, pk):
    escort = get_object_or_404(Escort, pk=pk)
    if request.method == 'POST':
        rating_value = float(request.POST.get('rating', 0.0))
        Rating.objects.update_or_create(
            escort=escort,
            user=request.user,
            defaults={'value': rating_value}
        )
        return redirect('escort_detail', pk=pk)
    return render(request, 'directory/escort_detail.html', {'escort': escort})

@login_required
def escort_create(request):
    if request.method == 'POST':
        form = EscortForm(request.POST, request.FILES)
        if form.is_valid():
            escort = form.save(commit=False)
            escort.user = request.user
            escort.save()
            messages.success(request, 'Escort created successfully!')
            return redirect('escort_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EscortForm()
    return render(request, 'directory/escort_create.html', {'form': form})

@login_required
def edit_escort_profile(request):
    if request.method == 'POST':
        form = EscortForm(request.POST, request.FILES)
        if form.is_valid():
            escort = form.save(commit=False)
            escort.user = request.user
            escort.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('escort_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EscortForm()
    return render(request, 'directory/edit_escort_profile.html', {'form': form})