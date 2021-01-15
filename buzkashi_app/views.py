from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from . import forms


def home_view(request, *args, **kwargs):
    return render(request, "index.html", {})


def challenges_view(request, *args, **kwargs):
    return render(request, "challenges.html", {})


def challenges_edit_view(request, *args, **kwargs):
    return render(request, "challenges-edit.html", {})


def rank_view(request, *args, **kwargs):
    return render(request, "rank.html", {})


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
