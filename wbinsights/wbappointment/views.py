from django.shortcuts import render, redirect

from web.models import Expert
from .forms import AppointmentForm

# Create your views here.


def add_appointment(request, *args, **kwargs):
    expert = Expert.objects.get(pk=kwargs['pk'])
    context = {
        "expert":expert
    }
    return render(request,"add_appointment.html", context=context)

def add_appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # assuming you have a success url mapped in your urls.py
    else:
        form = AppointmentForm()

    return render(request, 'appointment.html', {'form': form})
