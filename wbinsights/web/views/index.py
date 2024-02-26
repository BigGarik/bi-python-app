from django.shortcuts import render
from django.http import HttpResponseNotFound


def handleIndex(request):
    context = {
        "data": "data"
    }
    return render(request, "index.html", context)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
