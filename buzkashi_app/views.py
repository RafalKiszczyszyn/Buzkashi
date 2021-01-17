from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.forms import formset_factory
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from .forms import TaskEditForm, TeamForm, EduInstitutionSelectForm, RegistrationComplimentForm, ParticipantForm
from .models import Team, Task, Judge, Competition


def home_view(request, *args, **kwargs):
    return render(request, "index.html", {})


class TasksView(View):
    template_name = 'tasks/tasks.html'
    success_url = '/tasks'
    queryset = Task.objects.all()
    view_bag = {}

    def get(self, request):
        logged_judge = get_object_or_404(Judge, user=request.user)
        self.view_bag['tasks'] = Task.objects.filter(author=logged_judge)
        self.view_bag['competitions'] = Competition.objects.all()

        return render(request, self.template_name, self.view_bag)

    def post(self, request):
        task_id = int(request.POST.get('input-task-id'))
        competition_id = int(request.POST.get('select-comp'))

        updated_task = get_object_or_404(Task, id=task_id)
        competition = get_object_or_404(Competition, id=competition_id)

        updated_task.competition = competition
        updated_task.save()

        return self.get(request)


class TaskEditView(UpdateView):
    template_name = 'tasks/task_edit.html'
    form_class = TaskEditForm
    success_url = '/tasks'

    def get_object(self, **kwargs):
        id_ = self.kwargs.get("task_id")
        return get_object_or_404(Task, id=id_)

    def form_valid(self, form):
        return super().form_valid(form)


class TaskCreateView(CreateView):
    template_name = 'tasks/task_edit.html'
    form_class = TaskEditForm
    success_url = '/tasks'

    def form_valid(self, form):
        author = Judge.objects.get(user=self.request.user.id)

        obj = form.save(commit=False)
        obj.author = author
        obj.save()

        return super().form_valid(form)


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
    ParticipantFormSet = formset_factory(ParticipantForm, extra=3)

    def __init__(self, *args, **kwargs):
        super(RegistrationView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request):
        formset = self.ParticipantFormSet()
        self.__load_forms(formset)

        return render(request, self.template_name, self.context)

    def post(self, request):
        participant_formset = self.ParticipantFormSet(request.POST)
        team_form = TeamForm(request.POST)
        institution_form = EduInstitutionSelectForm(request.POST)
        compliment_form = RegistrationComplimentForm(request.POST)

        if self.__is_valid(participant_formset, team_form, institution_form, compliment_form):
            self.__save_models(participant_formset, team_form, institution_form, compliment_form)
            return redirect('home')

        self.__load_forms(participant_formset, team_form, institution_form, compliment_form)
        return render(request, self.template_name, self.context)

    def __is_valid(self, participant_formset, team_form, institution_form, compliment_form):
        is_valid = True

        # czy dane zawodników są poprawne
        if not participant_formset.is_valid():
            is_valid = False

        # czy zespół ma unikalną nazwę
        if not team_form.is_valid():
            is_valid = False

        # czy wybrano istniejącą placówkę edukacyjną
        if not institution_form.is_valid():
            is_valid = False

        institution = institution_form.cleaned_data['institution']
        # jezeli wybrano szkołę średnią sprawdź poprawność danych uzupełniających
        if not institution.is_university:
            compliment_form.set_valid_auth_code(institution.authorization_code)
            if not compliment_form.is_valid():
                self.context['need_compliment'] = True
                is_valid = False

        return is_valid

    @classmethod
    def __save_models(cls, participant_formset, team_form, institution_form, compliment_form):
        team = team_form.save(commit=False)
        institution = institution_form.cleaned_data['institution']

        if not institution.is_university:
            team.tutor = f"{compliment_form.cleaned_data['tutor_name']} " \
                         f"{compliment_form.cleaned_data['tutor_surname']}"
            team.priority = compliment_form.cleaned_data['priority']

        team.institution = institution

        participants = []
        for participant_form in participant_formset:
            participant = participant_form.save(commit=False)
            participant.team = team
            participants.append(participant)
        participants[0].is_capitan = True

        with transaction.atomic():
            team.save()
            for participant in participants:
                participant.save()

        return True

    def __load_forms(self, participants,
                     team=TeamForm(),
                     institution=EduInstitutionSelectForm(),
                     compliment=RegistrationComplimentForm()):

        self.context['management_form'] = participants.management_form
        self.context['captain'] = participants[0]
        self.context['participant1'] = participants[1]
        self.context['participant2'] = participants[2]
        self.context['team'] = team
        self.context['institution'] = institution
        self.context['compliment'] = compliment
