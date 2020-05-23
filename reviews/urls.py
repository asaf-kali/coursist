from django.urls import path

from reviews.views import AjaxView, CourseView, index, CoursesView

urlpatterns = [
    path("", index, name="index"),
    path("ajax/", AjaxView.as_view(), name="ajax"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("courses/<int:course_number>/", CourseView.as_view(), name="course-details"),
]
