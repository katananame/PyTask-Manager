from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.html import escape
from django.http import Http404, JsonResponse
from .models import Task
from .forms import TaskForm
from datetime import datetime


@csrf_protect
@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('task_list')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})


@csrf_protect
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                username_safe = escape(username)
                messages.success(request, f'Добро пожаловать, {username_safe}!')
                return redirect('task_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})


@csrf_protect
def user_logout(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')


@login_required
@never_cache
def task_list(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    tasks = Task.objects(user_id=request.user.id)
    
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=int(priority_filter))
    
    tasks = tasks.order_by('-created_at')
    
    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter
    })


@login_required
@csrf_protect
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            task = Task(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                status=status,
                priority=int(form.cleaned_data['priority']),
                user_id=request.user.id,
                completed=status == 'done',
                due_date=form.cleaned_data['due_date']
            )
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Создать'})


@login_required
@csrf_protect
def task_edit(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        messages.error(request, 'Задача не найдена.')
        return redirect('task_list')
    
    if task.user_id != request.user.id:
        messages.error(request, 'У вас нет прав для редактирования этой задачи.')
        return redirect('task_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            task.title = form.cleaned_data['title']
            task.description = form.cleaned_data['description']
            task.status = status
            task.priority = int(form.cleaned_data['priority'])
            task.completed = status == 'done'
            task.due_date = form.cleaned_data['due_date']
            task.save()
            messages.success(request, 'Задача успешно обновлена!')
            return redirect('task_list')
    else:
        initial_data = {
            'title': task.title,
            'description': task.description,
            'status': getattr(task, 'status', 'todo'),
            'priority': task.priority,
            'completed': task.completed,
            'due_date': task.due_date.strftime('%Y-%m-%dT%H:%M') if task.due_date else None
        }
        form = TaskForm(initial=initial_data)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Редактировать', 'task': task})


@login_required
@csrf_protect
def task_delete(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        messages.error(request, 'Задача не найдена.')
        return redirect('task_list')
    
    if task.user_id != request.user.id:
        messages.error(request, 'У вас нет прав для удаления этой задачи.')
        return redirect('task_list')
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задача успешно удалена!')
        return redirect('task_list')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
@csrf_protect
def task_toggle(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        messages.error(request, 'Задача не найдена.')
        return redirect('task_list')
    
    if task.user_id != request.user.id:
        messages.error(request, 'У вас нет прав для изменения этой задачи.')
        return redirect('task_list')
    
    task.completed = not task.completed
    task.save()
    messages.success(request, 'Статус задачи изменен!')
    return redirect('task_list')


@login_required
def task_autocomplete(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    tasks = Task.objects(
        user_id=request.user.id,
        title__icontains=query
    ).only('title').limit(10)
    
    suggestions = [task.title for task in tasks]
    
    return JsonResponse({'suggestions': suggestions})

