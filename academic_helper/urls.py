from django.urls import path, include

from academic_helper.views import (
    AjaxView,
    CourseDetailsView,
    index,
    CoursesView,
    AboutView,
    LoginView,
    SignupView,
    SearchView,
    FetchClassesView,
)

urlpatterns = [
    path("", index, name="index"),
    path("ajax/", AjaxView.as_view(), name="ajax"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("courses/<int:course_number>/", CourseDetailsView.as_view(), name="course-details"),
    path("accounts/", include("allauth.urls"), name="accounts"),
    path("about/", AboutView.as_view(), name="about"),
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("search", SearchView.as_view(), name="search_course"),
    path("fetch_classes", FetchClassesView.as_view(), name="fetch_classes"),
]
