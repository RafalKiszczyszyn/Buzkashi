from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import home_view, SolutionResultsView, SolutionCodeView, SolutionsView, \
    RegistrationView, TaskCreateView, TaskEditView, TasksView, comps_view, SolutionJudgementView, RankView

urlpatterns = [

    path('', home_view, name='home'),
    path('comps/', comps_view, name='comps'),
    path('tasks/', login_required(TasksView.as_view(), login_url='login'), name='tasks'),
    path('tasks/<int:task_id>', login_required(TaskEditView.as_view()), name='task_edit'),
    path('tasks/create/', login_required(TaskCreateView.as_view()), name='task_create'),
    path('rank/', RankView.as_view(), name='rank'),
    path('solutions/', login_required(SolutionsView.as_view()), name='solutions'),
    path('solutions/results/<int:solution_id>', login_required(SolutionResultsView.as_view()), name='solution_results'),
    path('solutions/code/<int:solution_id>', login_required(SolutionCodeView.as_view()), name='solution_code'),
    path('solutions/judgment/<int:solution_id>,<str:decision>', login_required(SolutionJudgementView.as_view()),
         name='solution_judgement'),
    path('registration', RegistrationView.as_view(), name='registration'),

]
