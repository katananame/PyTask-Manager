from django import forms
from datetime import datetime


class TaskForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        required=True,
        label='Название',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название задачи'})
    )
    description = forms.CharField(
        max_length=1000,
        required=False,
        label='Описание',
        widget=forms.Textarea(attrs={'placeholder': 'Введите описание задачи', 'rows': 4})
    )
    status = forms.ChoiceField(
        choices=[
            ('todo', 'Сделать'),
            ('in_progress', 'В работе'),
            ('done', 'Готово')
        ],
        initial='todo',
        label='Статус'
    )
    priority = forms.ChoiceField(
        choices=[
            (0, 'Низкий'),
            (1, 'Средний'),
            (2, 'Высокий')
        ],
        initial=0,
        label='Приоритет'
    )
    due_date = forms.DateTimeField(
        required=False,
        label='Срок выполнения',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

