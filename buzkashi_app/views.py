import csv
from datetime import timedelta
from io import StringIO


from django import forms
from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.forms import modelformset_factory
from django.db import transaction
from .forms import TeamForm, EduInstitutionSelectForm, RegistrationComplimentForm, ParticipantForm, TaskEditForm, \
    CompetitionSelectForm
from .models import Team, Task, Judge, Competition, Solution, AutomatedTest, AutomatedTestResult, Participant
from urllib.parse import urlencode


def home_view(request):
    return render(request, "index.html", {})


def comps_view(request):
    return render(request, "comps.html", {})


class TasksView(View):
    template_name = 'tasks/tasks.html'
    success_url = '/tasks'

    def __init__(self, *args, **kwargs):
        super(TasksView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request):
        logged_judge = get_object_or_404(Judge, user=request.user)
        self.context['tasks'] = Task.objects.filter(author=logged_judge)
        self.context['competitions'] = Competition.get_coming_competitions()

        return render(request, self.template_name, self.context)

    def post(self, request):
        task_id = int(request.POST.get('input-task-id'))
        competition_id = int(request.POST.get('select-comp'))

        updated_task = get_object_or_404(Task, id=task_id)

        if competition_id != 0:
            competition = get_object_or_404(Competition, id=competition_id)
        else:
            competition = None

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


class RankView(View):
    template_name = 'rank/rank.html'
    success_url = '/rank'

    def __init__(self):
        super(RankView, self).__init__()
        self.context = {}

    def get(self, request):
        competition = Competition.get_current_competition()

        if competition:
            end_date = competition.start_date + competition.duration - timedelta(hours=1)
            self.context['end_date'] = int(end_date.timestamp() * 1000)

            self.context['competition'] = competition
            rank = competition.rank.read().decode('utf-8')
            rank_frozen = competition.rank_frozen.read().decode('utf-8')

            if request.user.is_authenticated:
                self.context['rank'] = csv.reader(StringIO(rank), delimiter=',')
                self.context['rank_frozen'] = csv.reader(StringIO(rank_frozen), delimiter=',')
            else:
                if competition.is_frozen:
                    self.context['rank_frozen'] = csv.reader(StringIO(rank_frozen), delimiter=',')
                else:
                    self.context['rank'] = csv.reader(StringIO(rank), delimiter=',')

        return render(request, self.template_name, self.context)


class SolutionsView(View):
    template_name = 'solutions/solutions.html'

    def __init__(self, *args, **kwargs):
        super(SolutionsView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request):
        competition = Competition.get_current_competition()
        if competition:
            self.context['competition_title'] = competition.title
        else:
            return render(request, self.template_name, self.context)

        solutions = Solution.objects.select_related('author__competition') \
            .filter(judge_id=request.user.id).filter(status=Solution.SolutionStatus.PENDING)

        self.context['solutions'] = solutions

        return render(request, self.template_name, self.context)


class SolutionResultsView(View):
    template_name = 'solutions/solution_results.html'

    def __init__(self, *args, **kwargs):
        super(SolutionResultsView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request, solution_id):
        try:
            solution = Solution.objects.select_related('author').get(id=solution_id)
        except Solution.DoesNotExist:
            return HttpResponse(status=404)

        results = AutomatedTestResult.objects.select_related('test').filter(solution=solution)

        self.context['solution'] = solution
        self.__unpack_results(results)

        return render(request, self.template_name, self.context)

    def __unpack_results(self, results):
        unpacked = []
        for result in results:
            title = result.test.title

            result.test.expected_output.open('r')
            expected_output = result.test.expected_output.read()
            result.test.expected_output.close()

            result.output.open('r')
            output = result.output.read()
            result.output.close()

            unpacked.append((title, expected_output, output))

        self.context['results'] = unpacked


class SolutionCodeView(View):
    template_name = 'solutions/solution_code.html'

    def __init__(self, *args, **kwargs):
        super(SolutionCodeView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request, solution_id):
        try:
            solution = Solution.objects.select_related('author').get(id=solution_id)
        except Solution.DoesNotExist:
            return HttpResponse(status=404)

        solution.source_code.open('r')
        self.context['source_code'] = solution.source_code.read()
        solution.source_code.close()

        self.context['solution'] = solution

        return render(request, self.template_name, self.context)


class SolutionJudgementView(View):

    def get(self, request, solution_id, decision):
        try:
            solution = Solution.objects.select_related('author').get(id=solution_id)
        except Solution.DoesNotExist:
            return HttpResponse(status=404)

        if decision == 'accept':
            solution.status = Solution.SolutionStatus.ACCEPTED
            solution.author.score += solution.score
        elif decision == 'reject':
            solution.status = Solution.SolutionStatus.REJECTED
        elif decision == 'disqualify':
            solution.status = Solution.SolutionStatus.REJECTED
            solution.author.is_disqualified = True
        else:
            return HttpResponse(status=404)

        solution.save()
        return redirect('solutions')


class RegistrationView(View):
    template_name = 'registration/registration.html'
    ParticipantFormSet = modelformset_factory(model=Participant, form=ParticipantForm, extra=3)

    def __init__(self, *args, **kwargs):
        super(RegistrationView, self).__init__(*args, **kwargs)
        self.context = {}
        self.redirect_context = {}

    def get(self, request):
        formset = self.ParticipantFormSet()
        self.__load_forms(formset)

        return render(request, self.template_name, self.context)

    def post(self, request):
        participant_formset = self.ParticipantFormSet(request.POST)
        team_form = TeamForm(request.POST)
        institution_form = EduInstitutionSelectForm(request.POST)
        competition_form = CompetitionSelectForm(request.POST)
        compliment_form = RegistrationComplimentForm(request.POST)

        if self.__is_valid(participant_formset, team_form, institution_form, competition_form, compliment_form):
            self.__save_models(participant_formset, team_form, institution_form, competition_form, compliment_form)
            return redirect(f"{reverse('registration_success')}?{urlencode(self.redirect_context)}")

        self.__load_forms(participant_formset, team_form, institution_form, competition_form, compliment_form)
        return render(request, self.template_name, self.context)

    def __is_valid(self, participant_formset, team_form, institution_form, competition_form, compliment_form):
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

        if not competition_form.is_valid():
            is_valid = False
        competition = competition_form.cleaned_data['competition']

        if (competition.session != Competition.Session.UNIVERSITY_SESSION and institution.is_university)\
                or (competition.session == Competition.Session.UNIVERSITY_SESSION and not institution.is_university):
            is_valid = False
            self.context['competition_error'] = 'Nieodpowiednie zawody dla wybranej placówki edukacyjnej'

        # jezeli wybrano szkołę średnią sprawdź poprawność danych uzupełniających
        if not institution.is_university:
            compliment_form.set_valid_auth_code(institution.authorization_code)
            if not compliment_form.is_valid():
                self.context['need_compliment'] = True
                is_valid = False
        print(institution.is_university)

        return is_valid

    def __save_models(self, participant_formset, team_form, institution_form, competition_form, compliment_form):
        team = team_form.save(commit=False)
        institution = institution_form.cleaned_data['institution']
        competition = competition_form.cleaned_data['competition']

        if not institution.is_university:
            team.tutor = f"{compliment_form.cleaned_data['tutor_name']} " \
                         f"{compliment_form.cleaned_data['tutor_surname']}"
            team.priority = compliment_form.cleaned_data['priority']

        team.institution = institution
        team.competition = competition

        participants = participant_formset.save(commit=False)
        participants[0].is_capitan = True
        #with transaction.atomic():
        #    team.save()
        #    for participant in participants:
        #        participant.team = team
        #        participant.save()

        self.redirect_context['team_name'] = team.name
        self.redirect_context['competition_title'] = competition.title
        self.redirect_context['competition_start_date'] = competition.start_date
        self.redirect_context['captain_email'] = participants[0].email

        return True

    def __load_forms(self, participants,
                     team=TeamForm(),
                     institution=EduInstitutionSelectForm(),
                     competition=CompetitionSelectForm(),
                     compliment=RegistrationComplimentForm()):

        self.context['management_form'] = participants.management_form
        self.context['captain'] = participants[0]
        self.context['participant1'] = participants[1]
        self.context['participant2'] = participants[2]
        self.context['team'] = team
        self.context['institution'] = institution
        self.context['competition'] = competition
        self.context['compliment'] = compliment


def registration_success_view(request):
    context = {}
    for key in request.GET:
        print(type(request.GET[key]), request.GET[key])
        context[key] = request.GET[key]
    return render(request, 'registration/success.html', context)
