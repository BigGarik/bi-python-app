from django.shortcuts import render


def wb400handler(request, exception):
    return render(request, '404.html', status=404)