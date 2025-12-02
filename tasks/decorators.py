from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Task


def task_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, task_id, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            messages.error(request, 'Задача не найдена.')
            return redirect('task_list')
        
        if task.user_id != request.user.id:
            messages.error(request, 'У вас нет прав для выполнения этого действия.')
            return redirect('task_list')
        
        return view_func(request, task_id, *args, **kwargs)
    
    return wrapper

