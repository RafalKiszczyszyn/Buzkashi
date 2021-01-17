from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import home_view, rank_view,  SolutionResultsView, SolutionCodeView, SolutionsView, \
    RegistrationView, TaskCreateView, TaskEditView, TasksView, comps_view

urlpatterns = [

    path('', home_view, name='home'),
    path('comps/', comps_view, name='comps'),
    path('tasks/', login_required(TasksView.as_view()), name='tasks'),
    path('tasks/<int:task_id>', login_required(TaskEditView.as_view()), name='task_edit'),
    path('tasks/create/', login_required(TaskCreateView.as_view()), name='task_create'),
    path('rank/', rank_view, name='rank'),
    path('solutions/', SolutionsView.as_view(), name='solutions'),
    path('solutions/results/<int:solution_id>', SolutionResultsView.as_view(), name='solution_results'),
    path('solutions/code/<int:solution_id>', SolutionCodeView.as_view(), name='solution_code'),
    path('registration', RegistrationView.as_view(), name='registration'),

]
