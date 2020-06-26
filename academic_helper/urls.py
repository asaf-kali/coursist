from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path, include

from academic_helper.views.basic import IndexView
from academic_helper.views.courses import CoursesView, CourseDetailsView
from academic_helper.views.other import AjaxView, AboutView
from academic_helper.views.schedule import ScheduleView
from academic_helper.views.user_view import UserView


def healthy(request):
    return JsonResponse({"status": 200})


urlpatterns = [
    path("", redirect('courses'), name="index"),
    path("ajax/", AjaxView.as_view(), name="ajax"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("courses/<int:course_number>/", CourseDetailsView.as_view(), name="course-details"),
    path("accounts/", include("allauth.urls"), name="accounts"),
    path("about/", AboutView.as_view(), name="about"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("user/<str:username>/", UserView.as_view(), name="user")
]
