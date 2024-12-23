from django.urls import path
from .views import (
    ProjectListCreateView, ProjectDetailView, 
    TaskListCreateView, TaskDetailView,
    CustomLoginView
)

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('login/', CustomLoginView.as_view(), name='login'),
]
