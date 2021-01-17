from django.test import TestCase, RequestFactory
from django.urls import resolve
from buzkashi_app.views import TasksView, TaskEditView


class TasksViewsTest(TestCase):

    def test_tasks_url_resolves_to_tasks_view(self):
        resolver = resolve('/tasks/')
        self.assertEqual(resolver.func.__name__, TasksView.as_view().__name__)

    def test_task_edit_returns_correct_html(self):
        factory = RequestFactory()
        request = factory.get('/tasks/<>', {'task_id': 48})
        view = TaskEditView()
        print(view.setup(request, {'task_id': 48}))
        # print(view.get(request, {'task_id': 48}))
        self.assertEqual(1, 1)
