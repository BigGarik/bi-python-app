from django.shortcuts import render

# custom 404 view
def custom_404(request, exception):
    return render(request, '404.html', status=404)