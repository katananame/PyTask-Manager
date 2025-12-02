from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Task


class TaskViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass456'
        )
        
        self.task1 = Task(
            title='Task User 1',
            description='Description 1',
            user_id=self.user1.id,
            priority=1,
            status='todo'
        )
        self.task1.save()
        
        self.task2 = Task(
            title='Task User 2',
            description='Description 2',
            user_id=self.user2.id,
            priority=2,
            status='in_progress'
        )
        self.task2.save()

    def test_task_list_requires_login(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_task_list_shows_only_user_tasks(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('task_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task User 1')
        self.assertNotContains(response, 'Task User 2')

    def test_task_create_requires_login(self):
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 302)

    def test_task_create_saves_correctly(self):
        self.client.login(username='user1', password='pass123')
        Task.objects.filter(title='Unique New Task').delete()
        
        response = self.client.post(reverse('task_create'), {
            'title': 'Unique New Task',
            'description': 'New Description',
            'status': 'todo',
            'priority': '1',
            'due_date': ''
        })
        
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Unique New Task', user_id=self.user1.id)
        self.assertEqual(task.user_id, self.user1.id)
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.priority, 1)

    def test_task_edit_requires_owner(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(
            reverse('task_edit', args=[self.task2.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_list'))

    def test_task_edit_updates_correctly(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.post(
            reverse('task_edit', args=[self.task1.id]),
            {
                'title': 'Updated Task',
                'description': 'Updated Description',
                'status': 'in_progress',
                'priority': '2',
                'due_date': ''
            }
        )
        
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.title, 'Updated Task')
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.priority, 2)

    def test_task_delete_requires_owner(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.post(
            reverse('task_delete', args=[self.task2.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Task.objects.filter(id=self.task2.id)), 1)

    def test_task_delete_removes_task(self):
        self.client.login(username='user1', password='pass123')
        task_id = self.task1.id
        response = self.client.post(
            reverse('task_delete', args=[task_id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Task.objects.filter(id=task_id)), 0)

