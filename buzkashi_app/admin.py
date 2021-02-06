from django.contrib import admin

<<<<<<< HEAD
# Register your models here.
from buzkashi_app.models import Judge, Task, Team, Competition, Participant, EduInstitution, Solution, AutomatedTest, \
    AutomatedTestResult

admin.site.register(Competition)
admin.site.register(Team)
admin.site.register(Participant)
admin.site.register(EduInstitution)
admin.site.register(Task)
admin.site.register(Judge)
admin.site.register(Solution)
admin.site.register(AutomatedTest)
admin.site.register(AutomatedTestResult)
