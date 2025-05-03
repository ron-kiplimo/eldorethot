from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Escort, Rating

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