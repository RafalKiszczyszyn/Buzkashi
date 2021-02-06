import math

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta


class Competition(models.Model):
    """
    Klasa ORM zawodów.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    class Session(models.IntegerChoices):
        """
        Enumerator dla sesji zawodów.
        """

        UNIVERSITY_SESSION = 1
        HIGH_SCHOOL_SESSION = 2

    title = models.CharField(max_length=50, unique=True)
    """Unikalna nazwa zespołu."""

    session = models.IntegerField(choices=Session.choices, default=Session.UNIVERSITY_SESSION)
    """Sesja zawodów wybierana z enumeratora: Competition.Session."""

    start_date = models.DateTimeField(default=timezone.now)
    """Data rozpoczęcia zawodów. Domyślna wartość: timezone.now."""

    duration = models.DurationField(help_text='HH:MM:ss format', default=timedelta(hours=3))
    """Czas trwania zawodów. Domyśla wartość: timedelta(hours=3)."""

    max_teams = models.IntegerField(default=50)
    """Maksymalna liczba zespołów. Domyślna wartość: 50."""

    is_test = models.BooleanField(default=False)
    """Oznaczenie zawodów testowych. Domyślna wartość: False"""

    description = models.CharField(max_length=2000, blank=True, null=True)
    """Opis zawodów. Opcjonalne."""

    rank = models.FileField(upload_to='uploads/ranks', blank=True, null=True)
    """Ścieżka do pliku rankingu. Opcjonalne."""

    rank_frozen = models.FileField(upload_to='uploads/ranks', blank=True, null=True)
    """Ścieżka do pliku zamrożonego rankingu. Opcjonalne."""

    is_frozen = models.BooleanField(default=False)
    """Oznaczenie zamrożenia rankingu dla danych zawodów. Domyślna wartość: False"""

    @classmethod
    def get_coming_competitions(cls, registration_open=False):
        """
        Statyczna funkcja, która zwraca przyszłe zawody zaczynając od momentu wywołania.
        Jeżeli wartość registration_open jest równa True, zwraca tylko przyszłe zawody, na które otwarta jest
        rejestracja (tj. zaczynają się za tydzień i jeden dzień od momentu wywołania).

        :param registration_open: wyszukaj tylko przyszłe zawody otwarte na rejestracje.
        :return: query set z przyszłymi zawodami.
        """
        now = timezone.now()

        if registration_open:
            cur_date = datetime(year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo)
            search_from = cur_date + timedelta(weeks=1, days=1)
        else:
            search_from = now

        query_set = Competition.objects.filter(start_date__gt=search_from).order_by('start_date')
        return query_set

    @classmethod
    def get_current_competition(cls):
        """
        Statyczna funkcja, która zwraca obecnie odbywające się zawody.

        :return: model obecnie odbywających się zawodów.
        """
        now = timezone.now()
        cur_date = datetime(year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo)

        competition_set = Competition.objects.filter(start_date__range=(cur_date, cur_date + timedelta(days=1)))

        for _competition in competition_set:
            if _competition.start_date <= now <= _competition.start_date + _competition.duration:
                return _competition

        return None


class EduInstitution(models.Model):
    """
    Klasa ORM placówki edukacyjnej.
    Id generowane jest automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    name = models.CharField(max_length=50, unique=True)
    """Unikalna nazwa placówki edukacyjnej."""

    region = models.CharField(max_length=50)
    """Rejon placówki edukacyjnej."""

    email = models.EmailField(unique=True)
    """Unikalny adres email placówki edukacyjnej."""

    authorization_code = models.CharField(max_length=50, null=True, blank=True)
    """Kod autoryzacyjny. Wymagany dla szkół średnich. Opcjonalne."""

    is_university = models.BooleanField(default=True)
    """Oznaczenie uczelni wyższej. Wartość domyślna: True."""


class Team(models.Model):
    """
    Klasa ORM zespołu.
    Id jest generowane automatycznie.
    Jeżeli zespół został zakwalifikowany na zawody, przypisywane jest konto użytkownika.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    name = models.CharField(max_length=50, unique=True)
    """Unikalna nazwa zespołu."""

    score = models.DurationField(default=timedelta(seconds=0))
    """Ocena zespołu liczona w minutach. Domyślna wartość: 0min."""

    application_date = models.DateTimeField(default=timezone.now)
    """Data zgłoszenia zespołu. Domyślna wartość: timezone.now."""

    priority = models.IntegerField(default=1)
    """Priorytet. Domyślna wartość: 1."""

    is_qualified = models.BooleanField(default=False)
    """Oznaczenie zakwalifikowanego zespołu. Domyślna wartość: False."""

    is_disqualified = models.BooleanField(default=False)
    """Oznaczenie zdyskwalifikowanego zespołu. Domyślna wartość: False."""

    tutor = models.CharField(max_length=255, blank=True, null=True)
    """Imię i nazwisko opiekuna. Opcjonalne."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    """Konto użytkownika. Przypisywane tylko do zakwalifikowanego zespołu. Opcjonalne."""

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    """Zawody. Klucz obcy. Zespół jest usuwany kaskadowo."""

    institution = models.ForeignKey(EduInstitution, on_delete=models.PROTECT)
    """Placówka edukacyjna. Klucz obcy. Zespół chroniony podczas usuwania."""


class Participant(models.Model):
    """
    Klasa ORM uczestnika.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    name = models.CharField(max_length=50)
    """Imię zawodnika. Imię kapitana jest jednocześnie imieniem przypisanym do konta użytkownika."""

    surname = models.CharField(max_length=50)
    """Nazwisko zawodnika. Nazwisko kapitana jest jednocześnie nazwiskiem przypisanym do konta użytkownika."""

    email = models.EmailField()
    """Adres email zawodnika. Email kapitana jest jednocześnie emailem przypisanym do konta użytkownika."""

    is_capitan = models.BooleanField(default=False)
    """Oznaczenie kapitana. Domyślna wartość: False."""

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    """Zespół. Klucz obcy. Zawodnik jest usuwany kaskadowo."""


class Judge(models.Model):
    """
    Klasa ORM sędziego.
    Id konta użytkownika jest jednocześnie id sędziego.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    is_chief = models.BooleanField(default=False)
    """Oznaczenie głównego sędziego. Domyślna wartość: False."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    """Powiązane konto użytkownika. Klucz główny. Sędzia jest usuwany kaskadowo."""


class Task(models.Model):
    """
    Klasa ORM zadania.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    title = models.CharField(max_length=255, unique=True,
                             error_messages={"unique": "Zadanie o tym tytule już istnieje"})
    """Unikalny tytuł zadania."""

    body = models.TextField(max_length=2000)
    """Treść zadania."""

    author = models.ForeignKey(Judge, on_delete=models.CASCADE)
    """Autor - sędzia. Klucz obcy. Zadanie jest usuwane kaskadowo."""

    competition = models.ForeignKey(Competition, blank=True, null=True, default=None, on_delete=models.PROTECT)
    """Zawody. Klucz obcy. Zadanie jest chronione podczas usuwania. Opcjonalne."""

    def get_absolute_url(self):
        return reverse("task_edit", kwargs={"task_id": self.id})


class Solution(models.Model):
    """
    Klasa ORM rozwiązania.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    class ProgrammingLanguage(models.TextChoices):
        """
        Enumerator dla języka programowania.
        """

        JAVA = 'JAVA'
        CPP = 'C++'
        CS = 'C#'
        PYTHON = 'PYTHON'

    class SolutionStatus(models.TextChoices):
        """
        Enumerator dla statusu rozwiązania.
        """

        INCORRECT = 'Błędne'
        PENDING = 'Oczekujące'
        ACCEPTED = 'Zaakceptowane'
        REJECTED = 'Odrzucone'

    source_code = models.FileField(upload_to='uploads/solutions')
    """Ścieżka do pliku kodu źródłowego rozwiązania."""

    programming_language = models.TextField(choices=ProgrammingLanguage.choices, default=ProgrammingLanguage.JAVA)
    """Język programowania wybierany z enumeratora: Solution.ProgrammingLanguage. Domyślna wartość: JAVA."""

    author = models.ForeignKey(Team, on_delete=models.CASCADE)
    """Autor - drużyna. Klucz obcy. Rozwiązanie jest usuwane kaskadowo."""

    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)
    """Sędzia. Klucz obcy. Rozwiązanie jest usuwane kaskadowo."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    """Zadanie. Klucz obcy, Rozwiązanie jest usuwane kaskadowo."""

    status = models.TextField(choices=SolutionStatus.choices, null=True, blank=True)
    """Status rozwiązania wybierany z enumeratora: Solution.SolutionStatus. Opcjonalne."""

    version = models.IntegerField(default=1)
    """Wersja. Domyślna wartość: 1."""

    submission_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    """Czas złożenia. Domyślna wartość: timezone.now. Opcjonalne."""

    @property
    def submission_time_in_minutes(self):
        """
        Pomocnicze pole wyliczenione. Zwraca czas w minutach od rozpoczęcia zawodów do złożenia rozwiązania.
        Czas jest zaokrąglany w dół.
        """
        return math.floor((self.submission_time - self.author.competition.start_date).seconds / 60)

    @property
    def score(self):
        """
        Pole wyliczeniowe. Zwraca ocenę rozwiązania z uwzględniona karą.
        """
        return timedelta(minutes=self.submission_time_in_minutes + (self.version - 1) * 20)


class AutomatedTest(models.Model):
    """
    Klasa ORM testu automatycznego.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    title = models.CharField(max_length=255, null=True, blank=True)
    """Tytuł. Opcjonalne."""

    input = models.FileField(upload_to='uploads/tests', null=True, blank=True)
    """Ścieżka do pliku z wejściem programu. Opcjonalne."""

    expected_output = models.FileField(upload_to='uploads/tests')
    """Ścieżka do pliku z oczekiwanym wyjściem programu."""

    max_time = models.DurationField(default=timedelta(seconds=1))
    """Maksymalny czas wykonywania testu. Domyślna wartość: 1s."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    """Zadanie. Klucz obcy. Test automatyczny jest usuwany kaskadowo."""


class AutomatedTestResult(models.Model):
    """
    Klasa ORM wyniku testu automatycznego
    id generowane automatycznie
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    class TestStatus(models.IntegerChoices):
        """
        Enumerator dla statusu wyniku testu.
        """

        PASSED = 0
        TIME_EXCEEDED_ERROR = 1
        COMPILATION_ERROR = 2
        RUNTIME_ERROR = 3
        FAILED = 4

    output = models.FileField(upload_to='uploads/test_results')
    """Ścieżka do pliku z wyjściem programu."""

    status = models.IntegerField(choices=TestStatus.choices, default=TestStatus.FAILED)
    """Status testu wybierany z enumeratora: AutomatedTestResult.TestStatus. Domyślna wartość: FAILED."""

    runtime = models.DurationField()
    """Czas wykonywania testu."""

    test = models.ForeignKey(AutomatedTest, on_delete=models.CASCADE)
    """Test. Klucz obcy. Wynik testu automatycznego jest usuwany kaskadowo."""

    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    """Rozwiązanie. Klucz obcy. Wynik testu automatycznego jest usuwany kaskadowo."""


class Notice(models.Model):
    """
    Klasa ORM uwagi.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    title = models.CharField(max_length=50, default='')
    """Tytuł uwagi."""

    body = models.TextField(max_length=500, default='')
    """Treść."""

    publication_date = models.DateTimeField(default=timezone.now)
    """Data opublikowania. Domyślna wartość: timezone.now."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, default=None)
    """Zadanie. Klucz obcy. Uwaga jest usuwana kaskadowo."""

    author = models.ForeignKey(Team, on_delete=models.PROTECT, default=None)
    """Autor - drużyna. Klucz obcy. Uwaga jest chroniona podczas usuwania."""


class Explanation(models.Model):
    """
    Klasa ORM wyjaśnienia.
    Id jest generowane automatycznie.
    """

    objects = models.Manager
    """Domyślny menadżer dla modelu. Menadżer umożliwia tworzenie zapytań do bazy danych."""

    body = models.TextField(default=None)
    """Treść"""

    publication_date = models.DateTimeField(default=timezone.now)
    """Data opublikowania. Domyślna wartość: timezone.now."""

    judge = models.ForeignKey(Judge, on_delete=models.CASCADE, default=None)
    """Sędzia. Klucz obcy: Wyjaśnienie jest usuwane kaskadowo."""

    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, default=None)
    """Uwaga. Klucz obcy: Wyjaśnienie jest usuwane kaskadowo."""
