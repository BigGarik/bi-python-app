from django.urls import path
from .views import UserProjectCreateView, UserProjectDetailView

urlpatterns = [
    path('project_add/', UserProjectCreateView.as_view(), name='project_add'),
    path('project_detail/<slug:slug>/', UserProjectDetailView.as_view(), name='project_detail'),

    ]
