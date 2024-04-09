from django.urls import path
from .views import UserProjectCreateView, UserProjectDetailView, UserProjectUpdateView, UserProjectDeleteView, \
    project_file_delete

urlpatterns = [
    path('project/add/', UserProjectCreateView.as_view(), name='project_add'),
    path('project/<slug:slug>/', UserProjectDetailView.as_view(), name='project_detail'),
    path('project/<slug:slug>/edit/', UserProjectUpdateView.as_view(), name='project_edit'),
    path('project/<slug:slug>/delete/', UserProjectDeleteView.as_view(), name='project_delete'),
    path('project/file/<int:pk>/delete/', project_file_delete, name='project_file_delete'),

]
