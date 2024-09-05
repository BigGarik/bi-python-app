from django.urls import path
from .views import UserProjectCreateView, UserProjectDetailView, UserProjectUpdateView, UserProjectDeleteView, \
    project_file_delete, SearchExpertsAPIView, GetProjectsAPIView, GetProjectsView, update_hit_count

urlpatterns = [
    path('project/add/', UserProjectCreateView.as_view(), name='project_add'),
    path('project/<slug:slug>/', UserProjectDetailView.as_view(), name='project_detail'),
    path('project/<slug:slug>/edit/', UserProjectUpdateView.as_view(), name='project_edit'),
    path('project/<slug:slug>/delete/', UserProjectDeleteView.as_view(), name='project_delete'),
    path('project/file/<int:pk>/delete/', project_file_delete, name='project_file_delete'),
    path('search-experts/', SearchExpertsAPIView.as_view(), name='search_experts'),
    path('projects/json', GetProjectsAPIView.as_view(), name='projects'),
    path('projects/<int:project_id>/hit/', update_hit_count, name='update_hit_count'),
    path('projects/', GetProjectsView.as_view(), name='project-list'),
]
