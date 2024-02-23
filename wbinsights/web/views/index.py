from django.shortcuts import render
from django.http import HttpResponseNotFound




def handleIndex(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    context = {
        "data": "data"
    }
    # return render(request, "index.html", context)
    return render(request, "index.html", context)

def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")