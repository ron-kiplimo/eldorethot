from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Escort, Rating
from .forms import RegisterForm, EscortForm
from directory import models


def escort_list(request):
    query = request.GET.get('q')
    if query:
        escorts = Escort.objects.filter(Q(name__icontains=query) | Q(city__icontains=query))
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
        try:
            rating_value = float(request.POST.get('rating'))
            if not 0 <= rating_value <= 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value. Must be between 0 and 5.')
            return redirect('escort_detail', pk=pk)

        Rating.objects.update_or_create(
            escort=escort,
            user=request.user,
            defaults={'value': rating_value}
        )
        messages.success(request, 'Rating submitted successfully.')
        return redirect('escort_detail', pk=pk)

    user_rating = Rating.objects.filter(escort=escort, user=request.user).first()
    average_rating = Rating.objects.filter(escort=escort).aggregate(avg_rating=models.Avg('value'))['avg_rating']
    return render(request, 'directory/escort_detail.html', {
        'escort': escort,
        'user_rating': user_rating,
        'average_rating': average_rating or 0
    })


@login_required
def escort_create(request):
    if Escort.objects.filter(user=request.user).exists():
        messages.info(request, 'You already have an escort profile.')
        return redirect('edit_escort_profile')

    if request.method == 'POST':
        form = EscortForm(request.POST, request.FILES)
        if form.is_valid():
            escort = form.save(commit=False)
            escort.user = request.user
            escort.save()
            messages.success(request, 'Escort profile created successfully.')
            return redirect('escort_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EscortForm()

    return render(request, 'directory/escort_create.html', {'form': form})


@login_required
def edit_escort_profile(request):
    escort = get_object_or_404(Escort, user=request.user)

    if request.method == 'POST':
        form = EscortForm(request.POST, request.FILES, instance=escort)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('escort_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EscortForm(instance=escort)

    return render(request, 'directory/edit_escort_profile.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('escort_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'directory/register.html', {'form': form})
