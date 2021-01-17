from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import home_view, rank_view, solutions_view, solutions_results_view, solutions_code_view, \
    RegistrationView, TaskCreateView, TaskEditView, TasksView, comps_view

urlpatterns = [

    path('', home_view, name='home'),
    path('comps/', comps_view, name='comps'),
    path('tasks/', login_required(TasksView.as_view()), name='tasks'),
    path('tasks/<int:task_id>', login_required(TaskEditView.as_view()), name='task_edit'),
    path('tasks/create/', login_required(TaskCreateView.as_view()), name='task_create'),
    path('rank/', rank_view, name='rank'),
    path('solutions/', solutions_view, name='solutions'),
    path('solutions/results/<int:solution_id>', solutions_results_view, name='solutions_results'),
    path('solutions/code/<int:solution_id>', solutions_code_view, name='solutions_code'),
    path('registration', RegistrationView.as_view(), name='registration'),

]
