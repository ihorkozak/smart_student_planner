from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
from .models import Course, Task, Comment, WeatherCache
from .models import Tag, TaskTag
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def dashboard(request):
    if request.user.is_authenticated:
        upcoming_tasks = Task.objects.filter(
            user=request.user,
            is_completed=False,
            deadline__gte=timezone.now()
        ).order_by('deadline')[:5]

        overdue_tasks = Task.objects.filter(
            user=request.user,
            is_completed=False,
            deadline__lt=timezone.now()
        ).order_by('deadline')

        return render(request, 'dashboard.html', {
            'upcoming_tasks': upcoming_tasks,
            'overdue_tasks': overdue_tasks,
        })
    return render(request, 'dashboard.html')


@login_required
def course_list(request):
    courses = Course.objects.filter(user=request.user)
    return render(request, 'courses.html', {'courses': courses})

@login_required
def course_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        instructor = request.POST.get('instructor')
        schedule = request.POST.get('schedule')
        Course.objects.create(
            name=name,
            instructor=instructor,
            schedule=schedule,
            user=request.user
        )
        return redirect('course_list')
    return render(request, 'course_create.html')

@login_required
def course_delete(request, course_id):
    try:
        course = Course.objects.get(id=course_id, user=request.user)
        course.delete()
    except Course.DoesNotExist:
        pass
    return redirect('course_list')

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('is_completed', 'deadline')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_create(request):
    courses = Course.objects.filter(user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        if not title:
            return render(request, 'task_create.html', {'courses': courses})
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        priority = request.POST.get('priority')
        course_id = request.POST.get('course')
        course = Course.objects.get(id=course_id)
        Task.objects.create(
            title=title,
            description=description,
            deadline=deadline,
            priority=priority,
            course=course,
            user=request.user
        )
        return redirect('task_list')
    return render(request, 'task_create.html', {'courses': courses})

@login_required
def task_complete(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.is_completed = True
    task.save()
    return redirect('task_list')

@login_required
def task_delete(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.delete()
    return redirect('task_list')
@login_required
def comment_create(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(
            content=content,
            task=task,
            user=request.user
        )
    return redirect('task_detail', task_id=task_id)

@login_required
def task_detail(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    comments = Comment.objects.filter(task=task)
    return render(request, 'task_detail.html', {'task': task, 'comments': comments})


@login_required
def get_weather(request):
    city = request.GET.get('city', 'Kyiv')

    # перевіряємо чи є свіжий кеш (не старший 30 хвилин)
    cache = WeatherCache.objects.filter(
        user=request.user,
        city=city,
        fetched_at__gte=timezone.now() - timedelta(minutes=30)
    ).first()

    if not cache:
        url = "https://api.openweathermap.org/data/2.5/weather"
        response = requests.get(url, params={
            'q': city,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric'
        })
        data = response.json()

        cache = WeatherCache.objects.create(
            user=request.user,
            city=city,
            temperature=data['main']['temp'],
            condition=data['weather'][0]['description'],
        )

    return render(request, 'weather.html', {'weather': cache, 'city': city})
@login_required
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'tags.html', {'tags': tags})

@login_required
def tag_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.create(name=name)
        return redirect('tag_list')
    return render(request, 'tag_create.html')

@login_required
def task_add_tag(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    tags = Tag.objects.all()
    if request.method == 'POST':
        tag_id = request.POST.get('tag')
        tag = Tag.objects.get(id=tag_id)
        TaskTag.objects.get_or_create(task=task, tag=tag)
        return redirect('task_detail', task_id=task_id)
    return render(request, 'task_add_tag.html', {'task': task, 'tags': tags})

