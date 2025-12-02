from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.task_list, name='task_list'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<str:task_id>/edit/', views.task_edit, name='task_edit'),
    path('task/<str:task_id>/delete/', views.task_delete, name='task_delete'),
    path('task/<str:task_id>/toggle/', views.task_toggle, name='task_toggle'),
    path('api/task-autocomplete/', views.task_autocomplete, name='task_autocomplete'),
]

