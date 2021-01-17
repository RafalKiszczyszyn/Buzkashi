from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.


class Competition(models.Model):
    """
    Klasa ORM zawodów
    id generowane automatycznie
    """

    class Session(models.IntegerChoices):
        """
        Enumerator dla sesji zawodów
        """

        # sesja dla uczelni
        UNIVERSITY_SESSION = 1

        # sesja dla szkoły średniej
        HIGH_SCHOOL_SESSION = 2

    # nazwa: VARCHAR(50), NOT NULL, UNIQUE
    title = models.CharField(max_length=50, unique=True)

    # sesja: INTEGER, NOT NULL
    session = models.IntegerField(choices=Session.choices, default=Session.UNIVERSITY_SESSION)

    # data rozpoczęcia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    start_date = models.DateTimeField(default=timezone.now)

    # czas trwania: ???, NOT NULL
    duration = models.DurationField(help_text='HH:MM:ss format')

    # maksymalna liczba zespołów: INTEGER, NOT NULL, DEFAULT=50
    max_teams = models.IntegerField(verbose_name='Max Number Of Teams', default=50)

    # czy zawody testowe: BIT, NOT NULL
    is_test = models.BooleanField()

    # opis: VARCHAR(2000)
    description = models.CharField(max_length=2000, blank=True, null=True)

    # TODO: tutaj powinny być klucze obce do rankingu, ale nie wiadomo czy będzię on przechowywany w bazie


class EduInstitution(models.Model):
    """
    Klasa ORM placówki edukacyjnej
    id generowane automatycznie
    """

    # nazwa: VARCHAR(50), NOT NULL, UNIQUE
    name = models.CharField(max_length=50, unique=True)

    # wojewodztwo: VARCHAR(50), NOT NULL
    region = models.CharField(max_length=50)
    # TODO: enumerator?

    # email: VARCHAR(50), NOT NULL, UNIQUE
    email = models.EmailField(unique=True)

    # kod autoryzacji: VARCHAR(50)
    authorization_code = models.CharField(max_length=50, null=True, blank=True)

    # czy wyższa: BIT, NOT NULL
    is_university = models.BooleanField(default=True)


class Team(models.Model):
    """
    Klasa ORM zespołu
    id generowane automatycznie
    z modelem zespołu powiązane jest konto użytkownika
    """

    # nazwa: VARCHAR(50), NOT NULL, UNIQUE
    name = models.CharField(max_length=50, unique=True)

    # ocena: ???, NOT NULL, DEFAULT=0
    score = models.DurationField(default=0)

    # data zgłoszenia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    application_date = models.DateTimeField(default=timezone.now)

    # priorytet: INTEGER, NOT NULL, DEFAULT=0
    priority = models.IntegerField(default=0)

    # czy zakwalifikowany: BIT, NOT NULL
    is_qualified = models.BooleanField(default=False)

    # czy zdyskwalifikowany: BIT, NOT NULL
    is_disqualified = models.BooleanField(default=False)

    # opiekun: VARCHAR(255)
    tutor = models.CharField(max_length=255, blank=True, null=True)

    # powiązane konto
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # zawody: FOREIGN KEY(Competition)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    # placówka edukacyjna: FOREIGN KEY(EduInstitute)
    institution = models.ForeignKey(EduInstitution, on_delete=models.PROTECT)

    # TODO: tutaj powinien być klucz obcy do rankingu, ale nie wiadomo czy będzię on przechowywany w bazie


class Participant(models.Model):
    """
    Klasa ORM uczestnika
    id generowane automatycznie
    """

    # imię: VARCHAR(50), NOT NULL
    name = models.CharField(max_length=50)

    # nazwisko: VARCHAR(50), NOT NULL
    surname = models.CharField(max_length=50)

    # email: ???, NOT NULL
    email = models.EmailField()

    # czy kapitan: BIT, NOT NULL
    is_capitan = models.BooleanField(default=False)
    # TODO: ograniczenie w zespole: tylko jeden uczestnik moze byc kapitanem

    # zespół: FOREIGN KEY(Team)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Judge(models.Model):
    """
    Klasa ORM sędziego
    id generowane automatycznie
    z modelem sędziego powiązane jest konto użytkownika
    """

    # czy główny: BIT, NOT NULL
    is_chief = models.BooleanField(default=False)

    # powiązane konto
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Task(models.Model):
    """
    Klasa ORM zadania
    id generowane automatycznie
    """

    # tytuł: VARCHAR(255), NOT NULL, UNIQUE
    title = models.CharField(max_length=255)

    # treść: VARCHAR(2000), NOT NULL
    body = models.TextField(max_length=2000)

    # autor: FOREIGN KEY(Judge)
    author = models.ForeignKey(Judge, on_delete=models.CASCADE)

    # zawody: FOREIGN KEY(Competition)
    competition = models.ForeignKey(Competition, blank=True, null=True, default=None, on_delete=models.PROTECT)


class AutomatedTest(models.Model):
    """
    Klasa ORM testu automatycznego
    id generowane automatycznie
    """

    # tytuł: VARCHAR(255), NOT NULL
    title = models.CharField(max_length=255)

    # dane wejsciowe: FILE ?, NOT NULL TODO: jaka ścieżka zapisu?
    input = models.FileField(upload_to='uploads/tests')

    # oczekiwane dane wyjsciowe: FILE ?, NOT NULL
    expected_output = models.FileField(upload_to='uploads/tests')

    # max czas wykonywania: ???, NOT NULL, TODO: DEFAULT?
    max_time = models.DurationField(default=1)

    # zadanie: FOREIGN KEY(Task)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)


class AutomatedTestResult(models.Model):
    """
    Klasa ORM wyniku testu automatycznego
    id generowane automatycznie
    """

    class TestStatus(models.IntegerChoices):
        """
        Enumerator dla statusu wyniku testu
        """
        # zaakceptowane
        PASSED = 0

        # przekroczony czas wykonywania
        TIME_EXCEEDED_ERROR = 1

        # błąd kompilacji
        COMPILATION_ERROR = 2

        # błąd wykonywania
        RUNTIME_ERROR = 3

        # niezaakceptowane
        FAILED = 4

    # dane wyjściowe: FILE ?, NOT NULL
    output = models.FileField(upload_to='uploads/test_results')

    # status: INTEGER, NOT NULL, DEFAULT=4
    status = models.TextField(choices=TestStatus.choices, default=TestStatus.FAILED)

    # czas wykonywania: ???, NOT NULL
    runtime = models.DurationField()

    # test: FOREIGN KEY(AutomatedTest)
    test = models.ForeignKey(AutomatedTest, on_delete=models.CASCADE)

    # rozwiazanie: FOREIGN KEY(Solution)
    solution = models.ForeignKey(Task, on_delete=models.CASCADE)


class Solution(models.Model):
    """
    Klasa ORM rozwiązania
    id generowane automatycznie
    """

    class ProgrammingLanguage(models.TextChoices):
        """
        Enumerator dla języka programowania
        """

        JAVA = 'JAVA'
        CPP = 'C++'
        CS = 'C#'
        PYTHON = 'PYTHON'

    class SolutionStatus(models.TextChoices):
        """
        Enumerator dla statusu rozwiązania
        """

        # rozwiązanie błędne
        INCORRECT = 'Błędne'

        # rozwiązanie oczekujące zaakceptowania przez sędziego
        PENDING = 'Oczekujące'

        # rozwiązanie zaakceptowane
        ACCEPTED = 'Zaakceptowane'

        # rozwiązanie odrzucone
        REJECTED = 'Odrzucone'

    # kod źródłowy: FILE SAVED IN DIRECTORY NOT DATABASE!
    source_code = models.FileField(upload_to='uploads/solutions')

    # język programowania: ???, NOT NULL, DEFAULT='JAVA'
    programming_language = models.TextField(choices=ProgrammingLanguage.choices, default=ProgrammingLanguage.JAVA)

    # autor: FOREIGN KEY(Team)
    author = models.ForeignKey(Team, on_delete=models.CASCADE)

    # zadanie: FOREIGN KEY(Task)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    # status: ???
    status = models.TextField(choices=SolutionStatus.choices, null=True, blank=True)

    # wersja: INTEGER. NOT NULL, DEFAULT=1
    version = models.IntegerField(default=1)

    # czas złożenia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    submission_time = models.DateTimeField(default=timezone.now)

    # TODO: ocena wyliczana po zaakceptowaniu, uwzględnia czas złożenia i wersję


class Notice(models.Model):
    """
    Klasa ORM uwaga
    id generowane automatycznie
    """

    # tytuł: VARCHAR(50), NOT NULL
    title = models.CharField(max_length=50)

    # treść: ???(500), NOT NULL
    body = models.TextField(max_length=500)

    # data opublikowania: TIMESTAMP, NOT NULL, DEFAULT=NOW
    publication_date = models.DateTimeField(default=timezone.now)

    # zadanie: FOREIGN KEY(Task)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    # zespół: FOREIGN KEY(Team)
    author = models.ForeignKey(Team, on_delete=models.PROTECT)


class Explanation(models.Model):
    """
    Klasa ORM wyjaśnienie
    id generowane automatycznie
    """

    # treść: ???, NOT NULL
    body = models.TextField()

    # data opublikowania: TIMESTAMP, NOT NULL, DEFAULT=NOW
    publication_date = models.DateTimeField(default=timezone.now)

    # sędzia: FOREIGN KEY(Judge)
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)

    # uwaga: FOREIGN KEY(Notice)
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
