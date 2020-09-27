from django.http import JsonResponse
from django.urls import path, include

from academic_helper.views.basic import redirect_to_courses_view
from academic_helper.views.courses import CoursesView, CourseDetailsView, CourseListCreate
from academic_helper.views.degree_program import UserDegreeProgram
from academic_helper.views.other import AjaxView, AboutView
from academic_helper.views.schedule import ScheduleView
from academic_helper.views.user_view import UserView


def healthy(request):
    return JsonResponse({"status": 200})


urlpatterns = [
    # Old original views - to be deprecated
    path("", redirect_to_courses_view, name="index"),
    path("ajax/", AjaxView.as_view(), name="ajax"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("courses/<int:course_number>/", CourseDetailsView.as_view(), name="course-details",),
    path("accounts/", include("allauth.urls"), name="accounts"),
    path("about/", AboutView.as_view(), name="about"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("user/<str:username>/", UserView.as_view(), name="user"),
    path("degree-program/", UserDegreeProgram.as_view(), name="degree-program"),
    # New API views
    path("api/course/", CourseListCreate.as_view()),
]
