from django.urls import path
from .views import home_view, challenges_view, challenges_edit_view, rank_view, solutions_view,\
    solutions_results_view, solutions_code_view, RegistrationView


urlpatterns = [

    path('', home_view, name='home'),
    path('challenges/', challenges_view, name='challenges'),
    path('challenges-edit/', challenges_edit_view, name='challenges_edit'),
    path('rank/', rank_view, name='rank'),
    path('solutions/', solutions_view, name='solutions'),
    path('solutions/results/<int:solution_id>', solutions_results_view, name='solutions_results'),
    path('solutions/code/<int:solution_id>', solutions_code_view, name='solutions_code'),
    path('registration', RegistrationView.as_view(), name='registration'),

]
