from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from .models import Task
from .views import TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView, CustomLoginView, RegisterPageView


class TaskListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.seven_days_ago = self.today - timedelta(days=7)
        self.tomorrow = self.today + timedelta(days=1)
        self.task1 = Task.objects.create(title='Task 1', created=self.today, user=self.user)
        self.task2 = Task.objects.create(title='Task 2', created=self.yesterday, user=self.user)
        self.task3 = Task.objects.create(title='Task 3', created=self.seven_days_ago, user=self.user)
        self.task4 = Task.objects.create(title='Task 4', created=self.tomorrow, user=self.user)

    def test_task_list_view_with_search(self):
        url = reverse('task-list')
        response = self.client.get(url, {'search-title': 'Task 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')

    def test_task_list_view_with_filter_today(self):
        url = reverse('task-list')
        response = self.client.get(url, {'filter-option': 'today'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')

    def test_task_list_view_with_filter_yesterday(self):
        url = reverse('task-list')
        response = self.client.get(url, {'filter-option': 'yesterday'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')

    def test_task_list_view_with_filter_last_7_days(self):
        url = reverse('task-list')
        response = self.client.get(url, {'filter-option': 'last_7_days'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Task 4')
        self.assertContains(response, 'Task 2')
        self.assertContains(response, 'Task 3')

    def test_task_list_view_with_filter_tomorrow(self):
        url = reverse('task-list')
        response = self.client.get(url, {'filter-option': 'tomorrow'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')
        self.assertContains(response, 'Task 4')


class TaskDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.task = Task.objects.create(title='Task 1', created=date.today(), user=self.user)

    def test_task_detail_view(self):
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task.html')
        self.assertEqual(response.context['task'], self.task)


class TaskCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_task_create_view(self):
        url = reverse('task-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_form.html')

        data = {
            'title': 'New Task',
            'description': 'Test task',
            'complete': False,
            'created': date.today()
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('task-list'))
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().title, 'New Task')


class TaskUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.task = Task.objects.create(title='Task 1', created=date.today(), user=self.user)

    def test_task_update_view(self):
        url = reverse('task-update', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_form.html')

        data = {
            'title': 'Updated Task',
            'description': 'Updated task',
            'complete': True,
            'created': date.today()
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('task-list'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')


class TaskDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.task = Task.objects.create(title='Task 1', created=date.today(), user=self.user)

    def test_task_delete_view(self):
        url = reverse('task-delete', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_confirm_delete.html')

        response = self.client.post(url)
        self.assertRedirects(response, reverse('task-list'))
        self.assertFalse(Task.objects.exists())


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_custom_login_view(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/login.html')


class RegisterPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_view(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/register.html')

        data = {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('task-list'))
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
