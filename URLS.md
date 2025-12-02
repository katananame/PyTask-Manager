# Маршрутизация (URL-ы) проекта PyTask Manager

## Структура URL-ов

### Аутентификация

| URL | Имя маршрута | View | Описание |
|-----|--------------|------|----------|
| `/register/` | `register` | `register` | Регистрация нового пользователя |
| `/login/` | `login` | `user_login` | Вход в систему |
| `/logout/` | `logout` | `user_logout` | Выход из системы |

### Задачи (Tasks)

| URL | Имя маршрута | View | Описание | Требует авторизации |
|-----|--------------|------|----------|---------------------|
| `/` | `task_list` | `task_list` | Список всех задач пользователя | Да |
| `/task/create/` | `task_create` | `task_create` | Создание новой задачи | Да |
| `/task/<task_id>/edit/` | `task_edit` | `task_edit` | Редактирование существующей задачи | Да |
| `/task/<task_id>/delete/` | `task_delete` | `task_delete` | Удаление задачи | Да |
| `/task/<task_id>/toggle/` | `task_toggle` | `task_toggle` | Переключение статуса выполнения | Да |

### Администрирование

| URL | Имя маршрута | View | Описание |
|-----|--------------|------|----------|
| `/admin/` | - | Django Admin | Административная панель Django |

## Использование в шаблонах

```django
{% url 'task_list' %}
{% url 'task_create' %}
{% url 'task_edit' task.id %}
{% url 'task_delete' task.id %}
{% url 'task_toggle' task.id %}
{% url 'login' %}
{% url 'register' %}
{% url 'logout' %}
```

## Использование в Python коде

```python
from django.urls import reverse

reverse('task_list')
reverse('task_create')
reverse('task_edit', args=[task_id])
reverse('task_delete', args=[task_id])
reverse('task_toggle', args=[task_id])
```

## Параметры URL

- `<task_id>` - ID задачи (строка, ObjectId MongoDB)

## Защита маршрутов

Все маршруты для работы с задачами защищены декоратором `@login_required`.
Дополнительно проверяется принадлежность задачи пользователю.

