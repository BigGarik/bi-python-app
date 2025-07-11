"""
URL configuration for wbinsights project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from wbinsights import settings

urlpatterns = [
    path('', include('web.urls')),
    path('wbqa/', include('wbqa.urls')),
    path('expert/',include('expertprojects.urls')),
    path('appointment/', include('wbappointment.urls')),
    path(r'jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path(r'comments/', include('django_comments_xtd.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
