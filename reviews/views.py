from django.shortcuts import render
from django.utils import timezone

from reviews.models.course import Course


def home(request):
    all_courses = Course.all_courses()
    return render(request, "home.html", context={"courses": all_courses, "my_number": 8, "now": timezone.now()})
