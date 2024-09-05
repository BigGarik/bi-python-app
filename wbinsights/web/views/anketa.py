from django.shortcuts import render

from web.forms.anketa import ExpertAnketaForm


def user_profile_view(request):
    if request.method == 'POST':
        form = ExpertAnketaForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return render(request, 'template_name.html', {'data': data})
    else:
        form = ExpertAnketaForm()
    return render(request, 'template_name.html', {'form': form})
