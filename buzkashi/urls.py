"""buzkashi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from temp.views import home_view, challenges_view, challenges_edit_view, rank_view, solutions_view,\
    solutions_results_view, solutions_code_view, registration_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('challenges/', challenges_view, name='challenges'),
    path('challenges-edit/', challenges_edit_view, name='challenges_edit'),
    path('rank/', rank_view, name='rank'),
    path('solutions/', solutions_view, name='solutions'),
    path('solutions/results/<int:solution_id>', solutions_results_view, name='solutions_results'),
    path('solutions/code/<int:solution_id>', solutions_code_view, name='solutions_code'),
    path('registration', registration_view, name='registration'),
]
