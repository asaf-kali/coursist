from django.http import JsonResponse
from django.urls import path, include

from academic_helper.views.basic import index
from academic_helper.views.courses import CoursesView, CourseDetailsView
from academic_helper.views.other import AjaxView, AboutView, LoginView, SignupView
from academic_helper.views.schedule import ScheduleView


def healthy(request):
    return JsonResponse({"status": 200})


urlpatterns = [
    path("", index, name="index"),
    path("health/", healthy, name="health-check"),
    path("ajax/", AjaxView.as_view(), name="ajax"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("courses/<int:course_number>/", CourseDetailsView.as_view(), name="course-details"),
    path("accounts/", include("allauth.urls"), name="accounts"),
    path("about/", AboutView.as_view(), name="about"),
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
]
