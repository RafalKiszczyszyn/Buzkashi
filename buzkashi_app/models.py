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

    # data rozpoczęcia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    start_date = models.DateTimeField(default=timezone.now)

    # data zakończenia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    completion_date = models.DateTimeField(default=timezone.now)

    # czas trwania: FLOAT, NOT NULL
    duration = models.FloatField()

    # sesja: INTEGER, NOT NULL
    session = models.IntegerField(choices=Session.choices, default=Session.UNIVERSITY_SESSION)

    # maksymalna liczba zespołów: INTEGER, NOT NULL
    max_teams = models.IntegerField(verbose_name='Max Number Of Teams')

    # czy zawody testowe: BIT, NOT NULL
    test_run = models.BooleanField()

    # opis: VARCHAR(255)
    description = models.CharField(max_length=255, blank=True, null=True)

    # TODO: tutaj powinny być klucze obce do rankingu, ale nie wiadomo czy będzię on przechowywany w bazie


class EduInstitute(models.Model):
    """
    Klasa ORM placówki edukacyjnej
    id generowane automatycznie
    """
    pass


class Team(models.Model):
    """
    Klasa ORM zespołu
    id generowane automatycznie
    z modelem zespołu powiązane jest konto użytkownika
    """

    # nazwa: VARCHAR(50), NOT NULL, UNIQUE
    name = models.CharField(max_length=50, unique=True)

    # ocena: INTEGER, NOT NULL
    score = models.IntegerField()

    # czy zakwalifikowany: BIT, NOT NULL
    qualified = models.BooleanField()

    # czy zdyskwalifikowany: BIT, NOT NULL
    disqualified = models.BooleanField()

    # data zgłoszenia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    application_date = models.DateTimeField(default=timezone.now())

    # priorytet: INTEGER, NOT NULL DEFAULT=1
    priority = models.IntegerField(default=1)

    # opiekun: VARCHAR(255)
    guardian = models.CharField(max_length=255, blank=True, null=True)

    # powiązane konto
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE)

    # zawody: FOREIGN KEY(Competition)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    # placówka edukacyjna: FOREIGN KEY(EduInstitute)
    institute = models.ForeignKey(EduInstitute, on_delete=models.PROTECT)

    # TODO: tutaj powinien być klucz obcy do rankingu, ale nie wiadomo czy będzię on przechowywany w bazie


class Judge(models.Model):
    """
    Klasa ORM sędziego
    id generowane automatycznie
    z modelem sędziego powiązane jest konto użytkownika
    """

    # imię: VARCHAR(50), NOT NULL
    name = models.CharField(max_length=50)

    # nazwisko: VARCHAR(50), NOT NULL
    surname = models.CharField(max_length=50)

    # czy główny: BIT, NOT NULL
    chief = models.BooleanField()

    # powiązane konto
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE)


class Task(models.Model):
    """
    Klasa ORM zadania
    id generowane automatycznie
    """

    # nazwa: VARCHAR(255), NOT NULL
    name = models.CharField(max_length=255)

    # treść: VARCHAR(500), NOT NULL
    content = models.CharField(max_length=500)

    # opis: VARCHAR(255)
    description = models.CharField(max_length=255, blank=True, null=True)

    # autor: FOREIGN KEY(Judge)
    author = models.ForeignKey(Judge, on_delete=models.CASCADE)

    # zawody: FOREIGN KEY(Competition)
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)


class AutomaticTest(models.Model):
    """
    Klasa ORM testu automatycznego
    id generowane automatycznie
    """
    pass


class AutomaticTestResult(models.Model):
    """
    Klasa ORM wyniku testu automatycznego
    id generowane automatycznie
    """
    pass


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
    source_code = models.FileField()
