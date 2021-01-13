from django.shortcuts import render


def home_view(request, *args, **kwargs):
    return render(request, "index.html", {})


def challenges_view(request, *args, **kwargs):
    return render(request, "challenges.html", {})


def rank_view(request, *args, **kwargs):
    return render(request, "rank.html", {})