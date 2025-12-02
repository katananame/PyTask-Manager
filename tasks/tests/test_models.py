from django.test import TestCase
from django.contrib.auth.models import User
from tasks.models import Task
from datetime import datetime


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_task_creation(self):
        task = Task(
            title='Test Task',
            description='Test Description',
            user_id=self.user.id,
            priority=1,
            status='todo'
        )
        task.save()
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'Test Description')
        self.assertEqual(task.user_id, self.user.id)
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.status, 'todo')
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    def test_task_user_property(self):
        task = Task(
            title='Test Task',
            user_id=self.user.id
        )
        task.save()
        
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.user.username, 'testuser')

    def test_task_auto_update_timestamp(self):
        task = Task(
            title='Test Task',
            user_id=self.user.id
        )
        task.save()
        
        original_updated = task.updated_at
        task.title = 'Updated Task'
        task.save()
        
        self.assertNotEqual(task.updated_at, original_updated)
        self.assertEqual(task.title, 'Updated Task')

    def test_task_status_sync_with_completed(self):
        task = Task(
            title='Test Task',
            user_id=self.user.id,
            status='done',
            completed=True
        )
        task.save()
        
        self.assertTrue(task.completed)
        self.assertEqual(task.status, 'done')
        
        task.status = 'todo'
        task.completed = False
        task.save()
        
        self.assertFalse(task.completed)
        self.assertEqual(task.status, 'todo')

    def test_task_default_values(self):
        task = Task(
            title='Test Task',
            user_id=self.user.id
        )
        task.save()
        
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.priority, 0)
        self.assertFalse(task.completed)
        self.assertIsNone(task.due_date)

