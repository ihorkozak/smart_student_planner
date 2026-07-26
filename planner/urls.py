from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('dashboard'), name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/delete/<int:course_id>/', views.course_delete, name='course_delete'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/complete/<int:task_id>/', views.task_complete, name='task_complete'),
    path('tasks/delete/<int:task_id>/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/comment/', views.comment_create, name='comment_create'),
    path('weather/', views.get_weather, name='weather'),
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tasks/<int:task_id>/add-tag/', views.task_add_tag, name='task_add_tag'),
]