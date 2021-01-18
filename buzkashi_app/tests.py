from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import resolve, reverse
from buzkashi_app.models import Judge, Task
from buzkashi_app.views import TasksView

USERNAME = 'new'
PASSWORD = 'zawody2k21'


def create_user(username=USERNAME, password=PASSWORD):
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user


def create_judge():
    return Judge.objects.create(user=create_user())


def create_task(judge):
    return Task.objects.create(title='Nowe zadanie', body='Treść', author=judge)


def get_task_by_other_judge():
    user = create_user('nowy', PASSWORD)
    other_judge = Judge.objects.create(user=user)
    task = Task.objects.create(title='Inne zadanie', body='Treść', author=other_judge)
    return task


class ViewsTest(TestCase):

    def setUp(self) -> None:
        create_user()

        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_tasks_view_by_not_judge(self):
        response = self.client.get(reverse('tasks'))
        self.assertNotEqual(response.status_code, 200)


class ViewsTestJudge(TestCase):

    def setUp(self) -> None:
        self.judge = create_judge()

        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_tasks_url_resolves_to_tasks_view(self):
        resolver = resolve('/tasks/')
        self.assertEqual(resolver.func.__name__, TasksView.as_view().__name__)

    def test_tasks_view_by_judge(self):
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/tasks.html')

    def test_edit_task(self):
        task = create_task(self.judge)
        response = self.client.get(reverse('task_edit', args=[task.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_non_existent_task(self):
        response = self.client.get(reverse('task_edit', args=[0]))
        self.assertEqual(response.status_code, 404)

    def test_create_task(self):
        self.client.post(reverse('task_create'), {'title': "Nowe zadanie", 'body': "Treść", 'author': self.judge})
        self.assertEqual(Task.objects.last().title, "Nowe zadanie")
        self.assertEqual(Task.objects.last().body, "Treść")
