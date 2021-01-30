from django import forms
from . import models


class ParticipantForm(forms.ModelForm):
    """
    Klasa formularzu dla uczestnika
    """

    class Meta:
        """
        Klasa wskazująca, które pola z modelu zawodnika mają być połączone z formularzem
        """

        model = models.Participant
        fields = ['name', 'surname', 'email']

        labels = {
            'name': 'Imię',
            'surname': 'Nazwisko',
            'email': 'E-mail'
        }


class TeamForm(forms.ModelForm):
    """
    Klasa formularzu dla zespołu
    """

    class Meta:
        """
        Klasa wskazująca, które pola z modelu zespolu mają być powiązane z formularzem
        """

        model = models.Team
        fields = ['name']

        labels = {
            'name': 'Nazwa'
        }

        error_messages = {
            'name': {'unique': 'Wybrana nazwa jest już zajęta'}
        }


class EduInstitutionSelectForm(forms.Form):
    """
    Klasa formularzu wyboru placówki edukacyjnej
    """

    class EduInstitutionChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            """
            Nadpisuje sposób w jaki reprezentowany jest obiekt użytkownikowi

            @param obj: instancja modelu placówki edukacyjnej
            @return: 'nazwa, rejon'
            """
            return f"{obj.name}, {obj.region}"

    # placówka edukacyjna
    institution = EduInstitutionChoiceField(label='Nazwa', queryset=models.EduInstitution.objects.all())


class CompetitionSelectForm(forms.Form):

    class CompetitionChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return f'{obj.title}, ' \
                   f'{"uczelnie wyższe" if obj.session == models.Competition.Session.UNIVERSITY_SESSION else "szkoły średnie"}, ' \
                   f'{obj.start_date}'

    competition = CompetitionChoiceField(label='Zawody', queryset=models.Competition.get_coming_competitions())


class RegistrationComplimentForm(forms.Form):
    """
    Klasa formularzu danych uzupełniających rejestracje dla szkół średnich
    """

    # kod autoryzacyjny
    authorization_code = forms.CharField(label='Kod', max_length=50, required=False)

    # imię opiekuna
    tutor_name = forms.CharField(label='Imię', max_length=50, required=False)

    # nazwisko opiekuna
    tutor_surname = forms.CharField(label='Nazwisko', max_length=50, required=False)

    # priorytet zespołu
    priority = forms.IntegerField(label='Priorytet', min_value=1, required=False, initial=1,
                                  error_messages={0: 'Priorytet musi być większy od zera'})

    def __init__(self, *args, **kwargs):
        super(RegistrationComplimentForm, self).__init__(*args, **kwargs)
        self.valid_auth_code = None

    def set_valid_auth_code(self, valid_auth_code):
        self.valid_auth_code = valid_auth_code

    def clean(self):
        cleaned_data = super().clean()

        if self.valid_auth_code != cleaned_data['authorization_code']:
            self.add_error('authorization_code', 'Niepoprawny kod')


class TaskEditForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = [
            'title',
            'body'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-title',
                                            'placeholder': 'Tytuł zadania'}),
            'body': forms.Textarea(attrs={'class': 'input-text',
                                          'placeholder': 'Wprowadź treść zadania'}),
        }
        # TODO: utworzyć ograniczenia min i max length
