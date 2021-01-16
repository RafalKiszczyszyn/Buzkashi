from django.urls import path
from .views import home_view, tasks_view, task_edit_view, rank_view, solutions_view,\
    solutions_results_view, solutions_code_view, RegistrationView


urlpatterns = [

    path('', home_view, name='home'),
    path('tasks/', tasks_view, name='tasks'),
    path('task-edit/<int:task_id>', task_edit_view, name='task_edit'),
    path('rank/', rank_view, name='rank'),
    path('solutions/', solutions_view, name='solutions'),
    path('solutions/results/<int:solution_id>', solutions_results_view, name='solutions_results'),
    path('solutions/code/<int:solution_id>', solutions_code_view, name='solutions_code'),
    path('registration', RegistrationView.as_view(), name='registration'),

]
