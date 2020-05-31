import re

from allauth.account.views import LoginView as SuperLoginView, SignupView as SuperSignupView
from django.core import serializers
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from academic_helper.models.course import Course
from academic_helper.models.course_occurrence import CourseClass
from academic_helper.utils.logger import log


def index(request):
    return render(request, "index.html")


class ExtendedViewMixin(TemplateView):
    @property
    def title(self) -> str:
        base_name = self.__class__.__name__
        base_name = base_name.replace("View", "")
        return re.sub(r"(.)([A-Z])", "\\1 \\2", base_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def post(self, request: WSGIRequest):
        pass


class AjaxView(ExtendedViewMixin):
    template_name = "ajax.html"

    @property
    def title(self):
        return "Ajax"

    def post(self, request: WSGIRequest, *args, **kwargs):
        log.info("We are in POST")
        if request.is_ajax():
            value = "Hi " + request.POST["value"]
            log.info(f"User sent {value} via Ajax")
            return JsonResponse({"success": True, "value": value})
        else:
            value = request.POST["post-text"]
            log.info(f"User sent {value} via POST")
            return self.render_to_response(context={"value": value})


class CourseDetailsView(DetailView, ExtendedViewMixin):
    model = Course
    template_name = "course-details.html"

    @property
    def title(self) -> str:
        return f"Course {self.object.course_number}"

    @property
    def object(self):
        query = Course.objects.filter(course_number=self.kwargs["course_number"])
        return get_object_or_404(query)


# class CourseSearchForm(forms.Form):
#     free_text: forms.CharField(max_length=50)
#     faculty: forms.CharField(max_length=50)


class CoursesView(ExtendedViewMixin, ListView):
    model = Course
    template_name = "courses.html"

    @property
    def title(self) -> str:
        return "All Courses"

    @property
    def object_list(self):
        return Course.objects.all()

    def post(self, request: WSGIRequest):
        log.info("Courses POST")
        if not request.is_ajax():
            raise NotImplementedError()
        text = request.POST["free_text"]
        queryset = Course.find_by(text)
        result = [c.as_dict for c in queryset]
        return JsonResponse({"courses": result})


class AboutView(ExtendedViewMixin):
    template_name = "about.html"


class LoginView(SuperLoginView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["signup_url"] = reverse("signup")
        return context


class SignupView(SuperSignupView):
    template_name = "signup.html"


class ScheduleView(TemplateView):
    template_name = "schedule.html"

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
