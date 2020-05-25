from django.urls import path

from academic_helper.views import AjaxView, CourseDetailsView, index, CoursesView, AboutView

urlpatterns = [
    path("", index, name="index"),
    path("ajax/", AjaxView.as_view(), name="ajax"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("courses/<int:course_number>/", CourseDetailsView.as_view(), name="course-details"),
    path("about/", AboutView.as_view(), name="about"),
]
