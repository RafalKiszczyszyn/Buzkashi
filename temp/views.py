from django.shortcuts import render


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


def registration_view(request):
    return render(request, "registration.html", {})
