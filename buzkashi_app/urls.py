from django.urls import path
from .views import home_view, rank_view, RegistrationView, TaskCreateView, TaskEditView, TasksView, SolutionsView, \
    SolutionResultsView, SolutionCodeView

urlpatterns = [

    path('', home_view, name='home'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('tasks/<int:task_id>', TaskEditView.as_view(), name='task_edit'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('rank/', rank_view, name='rank'),
    path('solutions/', SolutionsView.as_view(), name='solutions'),
    path('solutions/results/<int:solution_id>', SolutionResultsView.as_view(), name='solution_results'),
    path('solutions/code/<int:solution_id>', SolutionCodeView.as_view(), name='solution_code'),
    path('registration', RegistrationView.as_view(), name='registration'),

]
