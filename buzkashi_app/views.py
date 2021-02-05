import csv
from datetime import timedelta
from io import StringIO

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
    """
    Klasa widoku dla zadań danego sędziego.
    Dostęp do widoku wymaga zalogowania.
    """
    template_name = 'tasks/tasks.html'
    success_url = '/tasks'

    def __init__(self, *args, **kwargs):
        super(TasksView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request):
        """
        Przygotowuje dla template listę zadań przypisanych do sędziego oraz listę przyszłych zawodów,
        do których można podpiąć zadania.
        Jeżeli zalogowany użytkownik nie jest sędzią, zwraca odpowiedź HTTP o statusie 404.

        :return: odpowiedź HTTP z templatem określonym w template_name i danymi zadań sędziego.
        """
        logged_judge = get_object_or_404(Judge, user=request.user)
        self.context['tasks'] = Task.objects.filter(author=logged_judge)
        self.context['competitions'] = Competition.get_coming_competitions()

        return render(request, self.template_name, self.context)

    def post(self, request):
        """
        Aktualizuje zadanie, do którego zostały podpięte zawody.
        Jeżeli zadanie lub zawody nie istnieją, zwraca odpowiedź HTTP o statusie 404.

        :return: odpowiedź HTTP z templatem określonym w template_name i zaktualizowanymi danymi zadań sędziego.
        """
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
    """
    Klasa widoku dla edycji zadania.
    Dostęp do widoku wymaga zalogowania.
    """
    template_name = 'tasks/task_edit.html'
    form_class = TaskEditForm
    success_url = '/tasks'

    def get_object(self, **kwargs):
        """
        Zwraca pojedynczy obiekt, którego dane zostaną wyświetlone.
        Jeżeli zadanie nie istnieje lub autorem nie jest zalogowany użytkownik, zwraca odpowiedź HTTP o statusie 404.

        :param kwargs: argumenty nazwane przekazane w URL, zmienna task_id określa id zadania.
        :return: obiekt zadania o id przekazanym w URL.
        """
        return get_object_or_404(Task, id=self.kwargs.get("task_id"), author=self.request.user.id)


class TaskCreateView(CreateView):
    """
    Klasa widoku dla tworzenia zadania.
    Dostęp do widoku wymaga zalogowania.
    """
    template_name = 'tasks/task_edit.html'
    form_class = TaskEditForm
    success_url = '/tasks'

    def form_valid(self, form):
        """
        Tworzy model zadania. Przypisuje aktualnie zalogowanego sędziego jako autora zadania.
        Zapisuje model.

        :param form: formularz widoku określony w form_class.
        :return: odpowiedź HTTP przekierowująca na success_url
        """
        author = Judge.objects.get(user=self.request.user.id)

        obj = form.save(commit=False)
        obj.author = author
        obj.save()

        return super().form_valid(form)


class RankView(View):
    """
    Klasa widoku rankingu.
    """
    template_name = 'rank/rank.html'

    def __init__(self):
        super(RankView, self).__init__()
        self.context = {}

    def get(self, request):
        """
        Przygotowuje dla template czas zakończenia zawodów i tablice rankingu dla aktualnie trwających zawodów.
        Jeżeli aktualnie nie odbywają się zawody, przekazuje pustą tablicę danych.
        Dane rankingów odczytuje z plików csv przypisanych zawodom.
        Jeżeli użytkownik wyświetlający ranking jest sędzią, przekazuje dane rankingu aktualnego i zamrożonego.
        W przeciwnym wypadku przekazuje dane jednego z nich, w zależności czy ranking jest zamrożony.

        :return: odpowiedź HTTP z templatem określonym w template_name.
        """
        competition = Competition.get_current_competition()

        if competition:
            end_date = competition.start_date + competition.duration - timedelta(hours=1)
            self.context['end_date'] = int(end_date.timestamp() * 1000)

            self.context['competition'] = competition
            rank = csv.reader(StringIO(competition.rank.read().decode('utf-8')), delimiter=',')
            rank_frozen = csv.reader(StringIO(competition.rank_frozen.read().decode('utf-8')), delimiter=',')

            if request.user.is_authenticated:
                self.context['rank'] = rank
                self.context['rank_frozen'] = rank_frozen
            else:
                if competition.is_frozen:
                    self.context['rank_frozen'] = rank_frozen
                else:
                    self.context['rank'] = rank

        return render(request, self.template_name, self.context)


class SolutionsView(View):
    """
    Klasa widoku dla rozwiązań oczekujących na zaakceptowanie.
    Dostęp do widoku wymaga zalogowania.
    """
    template_name = 'solutions/solutions.html'

    def __init__(self, *args, **kwargs):
        super(SolutionsView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request):
        """
        Przygotowuje dla template listę oczekujących rozwiązań przypisanych do sędziego oraz obecnie trwających zawodów.
        """
        competition = Competition.get_current_competition()
        if competition:
            self.context['competition_title'] = competition.title
        else:
            return render(request, self.template_name, self.context)

        solutions = Solution.objects.select_related('author__competition') \
            .filter(judge_id=request.user.id).filter(author__competition=competition) \
            .filter(status=Solution.SolutionStatus.PENDING)

        self.context['solutions'] = solutions

        return render(request, self.template_name, self.context)


class SolutionResultsView(View):
    """
    Klasa widoku dla wyników testów automatycznych wybranego rozwiązania.
    Dostęp do widoku wymaga zalogowania.
    """
    template_name = 'solutions/solution_results.html'

    def __init__(self, *args, **kwargs):
        super(SolutionResultsView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request, solution_id):
        """
        Przygotowuje dla template listę wyników testów automatycznych dla rozwiązania o podanym id.
        Jeżeli rozwiązanie nie istnieje, zwraca odpowiedź HTTP o statusie 404.

        :param solution_id: id rozwiązania.
        """
        try:
            solution = Solution.objects.select_related('author').get(id=solution_id)
        except Solution.DoesNotExist:
            return HttpResponse(status=404)

        results = AutomatedTestResult.objects.select_related('test').filter(solution=solution)

        self.context['solution'] = solution
        self.__unpack_results(results)

        return render(request, self.template_name, self.context)

    def __unpack_results(self, results):
        """
        Czyta zawartość plików przechowujących oczekiwane wyjście oraz aktualne wyjście progragramu po wykonanym teście.
        Przepakowuje zawartości plików do kontekstu widoku.

        :param results: lista wyników testów automatycznych.
        """
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
    """
    Klasa widoku dla podglądu kodu źródłowego wybranego rozwiązania.
    Dostęp do widoku wymaga zalogowania.
    """
    template_name = 'solutions/solution_code.html'

    def __init__(self, *args, **kwargs):
        super(SolutionCodeView, self).__init__(*args, **kwargs)
        self.context = {}

    def get(self, request, solution_id):
        """
        Przygotowuje dla template kod źródłowy rozwiązania o podanym id.
        Jeżeli rozwiązanie nie istnieje, zwraca odpowiedź HTTP o statusie 404.

        :param solution_id: id rozwiązania.
        """
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
    """
    Klasa widoku dla oceny wybranego rozwiązania.
    Dostęp do widoku wymaga zalogowania.
    """

    def get(self, request, solution_id, decision):
        """
        Na podstawie parametru decision akceptuje, odrzuca lub dyskwalifikuje rozwiązanie o podanym id.
        Jeżeli rozwiązanie nie istnieje lub wartość decision nie jest jedną z dozwolonych wartości,
        zwraca odpowiedź HTTP o statusie 404.

        :param solution_id: id rozwiązania.
        :param decision: "accept" lub "reject" lub "disqualify".
        """
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
            # disqualification procedure - not implemented
            pass
        else:
            return HttpResponse(status=404)

        solution.save()
        return redirect('solutions')


class RegistrationView(View):
    """
    Klasa widoku dla rejestracji.
    """

    template_name = 'registration/registration.html'
    ParticipantFormSet = modelformset_factory(model=Participant, form=ParticipantForm, extra=3)
    """
    Klasa zbioru trzech jednakowych formularzy dla zawodników.
    Wytworzona za pomoca fabryki django.forms.modelformset_factory.
    """

    def __init__(self, *args, **kwargs):
        super(RegistrationView, self).__init__(*args, **kwargs)
        self.institution = None
        self.competition = None
        self.context = {}
        self.redirect_context = {}

    def get(self, request):
        """
        Przygotowuje puste formularze uczestników, nazwy drużyny, wyboru placówki edukacyjnej, wyboru zawodów i
        pusty formularz uzupełniający dla template.
        """
        formset = self.ParticipantFormSet()
        self.__load_forms(formset)

        return render(request, self.template_name, self.context)

    def post(self, request):
        """
        Wypełnia formularze danymi przesłanymi wraz z żadaniem POST.
        Sprawdza poprawność formularzy oraz zgodność sesji zawodów z typem placówki edukacyjnej.
        Poprawność formularzu uzupełniającego jest sprawdzana, gdy wybraną placówką edukacyjną nie jest uczelnia wyższa.
        Jeżeli dane w formularzach są poprawne, zapisuje model zespołu, modele uczestników i zwraca przekierowanie
        HTTP na stronę z podsumowaniem.
        """
        formset = self.ParticipantFormSet(request.POST)
        team_form = TeamForm(request.POST)
        institution_form = EduInstitutionSelectForm(request.POST)
        competition_form = CompetitionSelectForm(request.POST)
        compliment_form = RegistrationComplimentForm(request.POST)

        if self.__is_valid(formset, team_form, institution_form, competition_form, compliment_form):
            self.__save_models(formset.save(commit=False), team_form.save(commit=False), compliment_form)
            return redirect(f"{reverse('registration_success')}?{urlencode(self.redirect_context)}")

        self.__load_forms(formset, team_form, institution_form, competition_form, compliment_form)
        return render(request, self.template_name, self.context)

    def __is_valid(self, participant_formset, team_form, institution_form, competition_form, compliment_form):
        """
        Sprawdza poprawność formularzy.
        Poprawność formularzu uzupełniającego jest sprawdzana, gdy wybraną placówką edukacyjną nie jest uczelnia wyższa.
        Sprawdza zgodność sesji zawodów z typem placówki edukacyjnej.

        :param participant_formset: zbiór formularzy dla uczestników.
        :param team_form: formularz nazwy drużyny.
        :param institution_form: formularz wyboru placówki edukacyjnej.
        :param competition_form: formularz wyboru zawodów.
        :param compliment_form: formularz uzypełniający.

        :return: True jeżeli wszystkie formularze są poprawne. False w przeciwnym wypadku.
        """
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
        self.institution = institution_form.cleaned_data['institution']

        if not competition_form.is_valid():
            is_valid = False
        self.competition = competition_form.cleaned_data['competition']

        if (self.competition.session != Competition.Session.UNIVERSITY_SESSION and self.institution.is_university) or \
                (
                        self.competition.session == Competition.Session.UNIVERSITY_SESSION and not self.institution.is_university):
            is_valid = False
            self.context['competition_error'] = 'Nieodpowiednie zawody dla wybranej placówki edukacyjnej'

        # jezeli wybrano szkołę średnią sprawdź poprawność danych uzupełniających
        if not self.institution.is_university:
            compliment_form.set_valid_auth_code(self.institution.authorization_code)
            if not compliment_form.is_valid():
                self.context['need_compliment'] = True
                is_valid = False

        return is_valid

    def __save_models(self, participants, team, compliment_form):
        """
        Tworzy modele uczestników i drużyny. Przypisuje drużynie wybrane zawody, placówkę edukacyjną oraz zawodników.
        Jeżeli wybrano szkołę średnią, przypisuje drużynie priorytet oraz opiekuna.
        Zapisuje modele.

        :param participants: lista modeli zawodników. Pierwszy zawodnik jest kapitanem.
        :param team: model drużyny.
        :param compliment_form: formularz uzupełniający.
        """
        if not self.institution.is_university:
            team.tutor = f"{compliment_form.cleaned_data['tutor_name']} " \
                         f"{compliment_form.cleaned_data['tutor_surname']}"
            team.priority = compliment_form.cleaned_data['priority']

        team.institution = self.institution
        team.competition = self.competition

        participants[0].is_capitan = True
        with transaction.atomic():
            team.save()
            for participant in participants:
                participant.team = team
                participant.save()

        self.redirect_context['team_name'] = team.name
        self.redirect_context['competition_title'] = self.competition.title
        self.redirect_context['competition_start_date'] = self.competition.start_date
        self.redirect_context['captain_email'] = participants[0].email

    def __load_forms(self, participants,
                     team=TeamForm(),
                     institution=EduInstitutionSelectForm(),
                     competition=CompetitionSelectForm(),
                     compliment=RegistrationComplimentForm()):
        """
        Przepakowuje formularze do kontekstu widoku.
        """
        self.context['management_form'] = participants.management_form
        self.context['captain'] = participants[0]
        self.context['participant1'] = participants[1]
        self.context['participant2'] = participants[2]
        self.context['team'] = team
        self.context['institution'] = institution
        self.context['competition'] = competition
        self.context['compliment'] = compliment


def registration_success_view(request):
    """
    Metoda widoku dla podsumowania poprawnej rejestracji.
    Dane podsumowania pobierane są z query string.
    """
    context = {}
    for key in request.GET:
        print(type(request.GET[key]), request.GET[key])
        context[key] = request.GET[key]
    return render(request, 'registration/success.html', context)
