from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from schedule.models import Course, CourseClass


class ScheduleView(TemplateView):
    template_name = "schedule/index.html"

    def get(self, request, *args, **kwargs):
        # Course.objects.all().delete()
        # CourseClass.objects.all().delete()
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            if "search_val" not in request.POST:
                return HttpResponseBadRequest()

            search_val = request.POST["search_val"]
            courses = Course.objects.filter(
                Q(name_he__icontains=search_val)
                | Q(name_en__icontains=search_val)
                | Q(course_number__icontains=search_val)
            ).order_by("course_number")[:10]

            json_courses = serializers.serialize("json", courses)

            return JsonResponse(
                {"status": "success", "course": json_courses}, json_dumps_params={"ensure_ascii": False},
            )  # TODO maybe remove


class SearchView(View):
    """
    View which searched and fetches the course by its number.
    If the course doesn't exist locally, we try to fetch it from Shnaton and
    add it to our database.
    """

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

        if "search_val" not in request.POST:
            return HttpResponseBadRequest()

        search_val = request.POST["search_val"]
        if not search_val.isdigit():
            return HttpResponseBadRequest()

        course = Course.objects.filter(course_number__exact=search_val)
        # TODO if count != 1 should be an error
        if course.count() == 0:
            # try fetching the course from Shnaton
            fetched_course = Course.fetch_course(search_val)
            if fetched_course is None:
                return JsonResponse({"status": "error", "msg": "Course not found"})

            json_course = serializers.serialize("json", fetched_course)
        else:
            json_course = serializers.serialize("json", course)

        return JsonResponse({"status": "success", "course": json_course})


class FetchClassesView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

        if "search_val" not in request.POST:
            return HttpResponseBadRequest()

        search_val = request.POST["search_val"]
        if not search_val.isdigit():
            return HttpResponseBadRequest()

        course = Course.objects.filter(course_number__exact=search_val)
        if course.count() != 1:
            return JsonResponse({"status": "error", "msg": "Course not found"})

        course_classes = CourseClass.objects.filter(course_id=course.first())
        json_classes = serializers.serialize("json", course_classes)

        return JsonResponse({"status": "success", "classes": json_classes})
