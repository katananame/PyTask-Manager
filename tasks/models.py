from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField
from datetime import datetime
from django.contrib.auth.models import User


class Task(Document):
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    completed = BooleanField(default=False)
    status = StringField(default='todo', choices=['todo', 'in_progress', 'done'])
    priority = IntField(default=0)
    user_id = IntField(required=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    due_date = DateTimeField(null=True)
    
    meta = {
        'collection': 'tasks',
        'ordering': ['-created_at'],
        'indexes': ['title', 'completed', 'status', 'priority', 'created_at', 'user_id']
    }
    
    def __str__(self):
        return self.title
    
    @property
    def user(self):
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
