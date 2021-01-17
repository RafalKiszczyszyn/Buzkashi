from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views import View

from . import forms
from .models import Team, Task, Judge


def home_view(request, *args, **kwargs):
    return render(request, "index.html", {})


def tasks_view(request):
    user_id = request.user.id
    try:
        judge_id = Judge.objects.get(user=user_id)
        obj = Task.objects.filter(author=judge_id)
    except:
        obj = Task.objects.all()
        print('YOU ARE NOT A JUDGE')
    context = {
        'tasks': obj
    }
    return render(request, "tasks/tasks.html", context)


def task_edit_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    form = forms.TaskEditForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()

    context = {
        'form': form
    }
    return render(request, "tasks/task_edit.html", context)


def task_create_view(request):
    form = forms.TaskEditForm(request.POST or None)

    if form.is_valid():
        author = Judge.objects.get(user=request.user.id)

        obj = form.save(commit=False)
        obj.author = author
        obj.save()

    context = {
        'form': form
    }
    return render(request, "tasks/task_edit.html", context)


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
