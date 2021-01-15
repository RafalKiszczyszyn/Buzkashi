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

    # data zakończenia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    end_date = models.DateTimeField(default=timezone.now)

    # czas trwania: FLOAT, NOT NULL
    duration = models.FloatField()
    #TODO: django ma typ DurationField

    # maksymalna liczba zespołów: INTEGER, NOT NULL
    max_teams = models.IntegerField(verbose_name='Max Number Of Teams')

    # czy zawody testowe: BIT, NOT NULL
    is_test = models.BooleanField()

    # opis: VARCHAR(255) TODO: chyba opis powinien być dłuższy
    description = models.CharField(max_length=255, blank=True, null=True)

    # TODO: tutaj powinny być klucze obce do rankingu, ale nie wiadomo czy będzię on przechowywany w bazie


class EduInstitution(models.Model):
    """
    Klasa ORM placówki edukacyjnej
    id generowane automatycznie
    """

    # nazwa: VARCHAR(50), NOT NULL, UNIQUE
    name = models.CharField(max_length=50, unique=True)

    # wojewodztwo: VARCHAR(50), NOT NULL, UNIQUE
    region = models.CharField(max_length=50, unique=True)
    # TODO: enumerator? chyba nie

    # email: VARCHAR(50), NOT NULL, UNIQUE
    email = models.CharField(max_length=50, unique=True)

    # kod autoryzacyjny: VARCHAR(50), NOT NULL
    authorization_code = models.CharField(max_length=50)

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

    # ocena: INTEGER, NOT NULL
    score = models.IntegerField(default=0)
    # TODO: ocena to suma czasu rozwiązywania zadań,
    #      więc chyba też mogłóby być to pole typu Duration

    # data zgłoszenia: TIMESTAMP, NOT NULL, DEFAULT=NOW
    application_date = models.DateTimeField(default=timezone.now)

    # priorytet: INTEGER, NOT NULL DEFAULT=1
    priority = models.IntegerField(default=1)

    # czy zakwalifikowany: BIT, NOT NULL
    is_qualified = models.BooleanField(default=False)

    # czy zdyskwalifikowany: BIT, NOT NULL
    is_disqualified = models.BooleanField(default=False)

    # opiekun: VARCHAR(255)
    tutor = models.CharField(max_length=255, blank=True, null=True)

    # powiązane konto
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE)

    # zawody: FOREIGN KEY(Competition)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    # placówka edukacyjna: FOREIGN KEY(EduInstitute)
    institution = models.ForeignKey(EduInstitution, on_delete=models.PROTECT)

    # TODO: tutaj powinien być klucz obcy do rankingu, ale nie wiadomo czy będzię on przechowywany w bazie
    # TODO: czy w zespole jest potrzebny ranking? Zespół mógłby odczytywać ranking przez Zawody


class Participant(models.Model):
    """
    Klasa ORM uczestnika
    id generowane automatycznie
    """

    # imię: VARCHAR(50), NOT NULL
    name = models.CharField(max_length=50)

    # nazwisko: VARCHAR(50), NOT NULL
    surname = models.CharField(max_length=50)
    # TODO: czy potrzebne są imiona, nazwiska i emaile
    #       jak uzytkownik auth je ma?

    # czy kapitan: BIT, NOT NULL
    is_capitan = models.BooleanField(default=False)

    # zespół: FOREIGN KEY(Team)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


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
    is_chief = models.BooleanField()

    # powiązane konto
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE)


class Task(models.Model):
    """
    Klasa ORM zadania
    id generowane automatycznie
    """

    # tytuł: VARCHAR(255), NOT NULL
    title = models.CharField(max_length=255)

    # treść: VARCHAR(500), NOT NULL
    body = models.CharField(max_length=500)
    # TODO: chyba wystarczy pole z treścią, nie potrzeba dodatkowo opisu?
    #       i też powinno być dłuższe

    # opis: VARCHAR(255)
    description = models.CharField(max_length=255, blank=True, null=True)

    # autor: FOREIGN KEY(Judge)
    author = models.ForeignKey(Judge, on_delete=models.CASCADE)

    # zawody: FOREIGN KEY(Competition)
    competition = models.ForeignKey(Competition, default=None, on_delete=models.PROTECT)


class AutomatedTest(models.Model):
    """
    Klasa ORM testu automatycznego
    id generowane automatycznie
    """
    pass


class AutomatedTestResult(models.Model):
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

    # author = models.ForeignKey(Team)
    #
    # task = models.ForeignKey(Task)
    #
    # version = models.IntegerField(default=1)
    #
    # time = models.FloatField()
    #
    # score = models.DurationField()
    # TODO: czy potrzebujemy osobnych pól na czas i ocenę?

    # kod źródłowy: FILE SAVED IN DIRECTORY NOT DATABASE!
    source_code = models.FileField()


