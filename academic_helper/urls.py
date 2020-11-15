from django.http import JsonResponse
from django.urls import path

from academic_helper.views.courses import CourseListCreate, CourseGet


def healthy(request):
    return JsonResponse({"status": 200})


urlpatterns = [
    # Old original views - to be deprecated
    # path("", redirect_to_courses_view, name="index"),
    # path("ajax/", AjaxView.as_view(), name="ajax"),
    # path("courses/", CoursesView.as_view(), name="courses"),
    # path("courses/<int:course_number>/", CourseDetailsView.as_view(), name="course-details",),
    # path("accounts/", include("allauth.urls"), name="accounts"),
    # path("about/", AboutView.as_view(), name="about"),
    # path("schedule/", ScheduleView.as_view(), name="schedule"),
    # path("user/<str:username>/", UserView.as_view(), name="user"),
    # path("degree-program/", UserDegreeProgram.as_view(), name="degree-program"),
    # New API views
    path("api/courses/", CourseListCreate.as_view()),
    path("api/courses/<int:pk>/", CourseGet.as_view()),
]
