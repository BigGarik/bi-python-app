from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse
from django.db import models

from django import forms


def handleIndex(request):
    context = {
        "data": "data"
    }
    return render(request, "index.html", context)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")





def handleTest(request):


    context = {
        "first_form": ""
    }

    return render(request, "test.html", context)
