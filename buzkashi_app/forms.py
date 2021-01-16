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
        fields = ['name', 'surname']

        labels = {
            'name': 'Imię',
            'surname': 'Nazwisko'
        }


class EduInstituteSelectForm(forms.Form):
    """
    Klasa formularzu wyboru placówki edukacyjnej
    """

    # placówka edukacyjna
    edu_institute = forms.ModelChoiceField(label='Nazwa', queryset=None)


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


class TaskForm(forms.ModelForm):
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
            # 'author': forms.Select(attrs={'disabled': True})
        }


# class TaskForm(forms.Form):
#     title = forms.CharField(widget=forms.TextInput(
#         attrs={
#             'class': 'input-title',
#             'placeholder': 'Tytuł zadania',
#         }))
#     body = forms.CharField(widget=forms.Textarea(
#         attrs={
#             'class': 'input-text',
#             'placeholder': 'Wprowadź treść zadania',
#         }
#     ))
