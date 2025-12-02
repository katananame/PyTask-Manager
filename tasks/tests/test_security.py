from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Task


class SecurityTest(TestCase):
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
            title='User1 Task',
            user_id=self.user1.id,
            priority=1
        )
        self.task1.save()
        
        self.task2 = Task(
            title='User2 Task',
            user_id=self.user2.id,
            priority=2
        )
        self.task2.save()

    def test_user_cannot_access_others_tasks(self):
        self.client.login(username='user1', password='pass123')
        
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'User1 Task')
        self.assertNotContains(response, 'User2 Task')

    def test_user_cannot_edit_others_task(self):
        self.client.login(username='user1', password='pass123')
        
        response = self.client.get(
            reverse('task_edit', args=[self.task2.id])
        )
        self.assertRedirects(response, reverse('task_list'))
        
        original_title = self.task2.title
        response = self.client.post(
            reverse('task_edit', args=[self.task2.id]),
            {
                'title': 'Hacked Task',
                'status': 'todo',
                'priority': '0',
                'due_date': ''
            }
        )
        
        task2_updated = Task.objects.get(id=self.task2.id)
        self.assertEqual(task2_updated.title, original_title)

    def test_user_cannot_delete_others_task(self):
        self.client.login(username='user1', password='pass123')
        
        response = self.client.post(
            reverse('task_delete', args=[self.task2.id])
        )
        
        self.assertEqual(len(Task.objects.filter(id=self.task2.id)), 1)
        self.assertRedirects(response, reverse('task_list'))

    def test_user_cannot_toggle_others_task(self):
        self.client.login(username='user1', password='pass123')
        
        original_completed = self.task2.completed
        response = self.client.get(
            reverse('task_toggle', args=[self.task2.id])
        )
        
        task2_updated = Task.objects.get(id=self.task2.id)
        self.assertEqual(task2_updated.completed, original_completed)
        self.assertRedirects(response, reverse('task_list'))

    def test_task_creation_assigns_correct_user(self):
        self.client.login(username='user1', password='pass123')
        Task.objects.filter(title='Unique User Task').delete()
        
        response = self.client.post(reverse('task_create'), {
            'title': 'Unique User Task',
            'status': 'todo',
            'priority': '1',
            'due_date': ''
        })
        
        task = Task.objects.get(title='Unique User Task', user_id=self.user1.id)
        self.assertEqual(task.user_id, self.user1.id)
        self.assertNotEqual(task.user_id, self.user2.id)

    def test_unauthorized_access_redirects(self):
        urls = [
            reverse('task_list'),
            reverse('task_create'),
            reverse('task_edit', args=[self.task1.id]),
            reverse('task_delete', args=[self.task1.id]),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)

