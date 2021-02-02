from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import resolve, reverse

from buzkashi_app.forms import RegistrationComplimentForm
from buzkashi_app.models import Judge, Task, Competition
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


def create_competition(title, start_date):
    return Competition.objects.create(title=title, start_date=start_date, is_test=False).id


def get_task_by_other_judge():
    user = create_user('nowy', PASSWORD)
    other_judge = Judge.objects.create(user=user)
    task = Task.objects.create(title='Inne zadanie', body='Treść', author=other_judge)
    return task


class TaskViewTest(TestCase):

    def setUp(self) -> None:
        create_user()

        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_tasks_view_by_not_judge(self):
        response = self.client.get(reverse('tasks'))
        self.assertNotEqual(response.status_code, 200)


class TasksViewJudgeTest(TestCase):

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


class CompetitionModelTest(TestCase):

    def test_get_current_competition(self):
        competition_model = Competition.get_current_competition()
        self.assertIsNone(competition_model)

        create_competition('Start in 1 minute', timezone.now() + timedelta(minutes=1))
        competition_model = Competition.get_current_competition()
        self.assertIsNone(competition_model)

        create_competition('Finished 1 minute ago', timezone.now() - timedelta(hours=3, minutes=1))
        competition_model = Competition.get_current_competition()
        self.assertIsNone(competition_model)

        _id = create_competition('Current', timezone.now())
        competition_model = Competition.get_current_competition()
        self.assertIsNotNone(competition_model)
        self.assertEqual(competition_model.id, _id)

    def test_get_coming_competitions(self):
        competition_set = Competition.get_coming_competitions()
        self.assertEqual(len(competition_set), 0)

        create_competition('Current', start_date=timezone.now())
        competition_set = Competition.get_coming_competitions(registration_open=False)
        self.assertEqual(len(competition_set), 0)

        _id1 = create_competition('Start in 1 week', start_date=timezone.now() + timedelta(weeks=1))
        competition_set = Competition.get_coming_competitions(registration_open=False)
        self.assertEqual(len(competition_set), 1)
        self.assertEqual(_id1, competition_set[0].id)

        competition_set = Competition.get_coming_competitions(registration_open=True)
        self.assertEqual(len(competition_set), 0)

        _id2 = create_competition('Start in 1 week and 1 day', start_date=timezone.now() + timedelta(weeks=1, days=1))
        competition_set = Competition.get_coming_competitions(registration_open=True)
        self.assertEqual(len(competition_set), 1)
        self.assertEqual(_id2, competition_set[0].id)


class RegistrationComplimentFormTest(TestCase):

    def test_not_required(self):
        form = RegistrationComplimentForm({})
        self.assertTrue(form.is_valid())

        form = RegistrationComplimentForm({'priority': 0})
        self.assertFalse(form.is_valid())

    def test_required_empty_form(self):
        form = RegistrationComplimentForm({})
        form.set_valid_auth_code('valid@code')
        self.assertFalse(form.is_valid())

        self.assertTrue(form.has_error('authorization_code'))
        self.assertTrue(form.has_error('tutor_name'))
        self.assertTrue(form.has_error('tutor_surname'))
        self.assertTrue(form.has_error('priority'))

    def test_required_invalid_auth_code(self):
        form = RegistrationComplimentForm({
            'authorization_code': 'invalid@code',
            'tutor_name': 'Rafał',
            'tutor_surname': 'Kiszczyszyn',
            'priority': 1
        })
        form.set_valid_auth_code('valid@code')
        self.assertFalse(form.is_valid())

        self.assertTrue(form.has_error('authorization_code'))

    def test_required_valid_auth_code(self):
        form = RegistrationComplimentForm({
            'authorization_code': 'valid@code',
            'tutor_name': 'Rafał',
            'tutor_surname': 'Kiszczyszyn',
            'priority': 1
        })
        form.set_valid_auth_code('valid@code')
        self.assertTrue(form.is_valid())
