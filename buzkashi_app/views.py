from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from . import forms
from .models import Team, Task


def home_view(request, *args, **kwargs):
    return render(request, "index.html", {})


def tasks_view(request):
    obj = Task.objects.all()
    context = {
        'tasks': obj
    }
    return render(request, "tasks.html", context)


def task_edit_view(request, task_id):
    obj = Task.objects.get(id=task_id)
    context = {
        'task': obj
    }
    return render(request, "task_edit.html", context)


def rank_view(request, *args, **kwargs):
    teams = Team.objects.all()
    context = {'teams': teams}
    return render(request, "rank.html", context)


def solutions_view(request):
    return render(request, "solutions.html", {})


def solutions_results_view(request, solution_id):
    return render(request, "solutions_results.html", {})


def solutions_code_view(request, solution_id):
    return render(request, "solutions_code.html", {})


class RegistrationView(View):

    template_name = 'registration.html'
    view_bag = {}

    def get(self, request):
        self.view_bag['captain'] = forms.ParticipantForm
        self.view_bag['compliment'] = forms.RegistrationComplimentForm()

        return render(request, self.template_name, self.view_bag)

    def post(self, request):
        captain = forms.ParticipantForm(request.POST)
        compliment = forms.RegistrationComplimentForm(request.POST)

        if captain.is_valid() and compliment.is_valid():
            return redirect(request, 'home')

        self.view_bag['captain'] = captain
        self.view_bag['compliment'] = compliment

        return render(request, self.template_name, self.view_bag)
