import logging

from django.core.handlers.wsgi import WSGIRequest
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.views.generic import DetailView, ListView

from academic_helper.logic import courses
from academic_helper.logic.errors import ShnatonParserError
from academic_helper.management.commands import fetch_course
from academic_helper.models import Course, Faculty, Department
from academic_helper.views.basic import ExtendedViewMixin

log = logging.getLogger(__name__)


class CourseDetailsView(DetailView, ExtendedViewMixin):
    model = Course
    template_name = "courses/course-details.html"

    @property
    def title(self) -> str:
        return f"{self.object.course_number} | {self.object.name}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["semester_rating_description"] = "כמה עמוס הקורס במהלך הסמסטר? כמה קשים שיעורי הבית? (1-קשה, 5-קל)"
        context["semester_rating_title"] = "סמסטר"
        context["exams_rating_description"] = "כמה קשה הבחינה/פרוייקט גמר? (1-קשה, 5-קל)"
        context["exams_rating_title"] = "בחינה"
        context["interest_rating_description"] = "כמה מעניין הקורס? כמה כיף? (1-לא מעניין, 5-מעניין)"
        context["interest_rating_title"] = "עניין"
        return context

    @property
    def object(self) -> Course:
        query = Course.objects.filter(course_number=self.kwargs["course_number"])
        return get_object_or_404(query)


class CoursesView(ExtendedViewMixin, ListView):
    model = Course
    template_name = "courses/courses.html"

    @property
    def title(self) -> str:
        return "All Courses"

    @property
    def object_list(self):
        return Course.objects.all()[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculties = Faculty.objects.values_list("name", flat=True)
        departments = Department.objects.values_list("name", flat=True)
        context["all_faculties"] = sorted(set(faculties))
        context["all_departments"] = sorted(set(d.replace(":", "").strip() for d in departments))
        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        if not request.is_ajax():
            raise NotImplementedError()
        text: str = request.POST["free_text"]
        department = request.POST["department"]
        faculty = request.POST["faculty"]
        queryset = courses.search(text, department, faculty)[:40]
        if len(queryset) == 0 and 4 <= len(text) <= 5 and text.isnumeric():
            try:
                result = call_command("fetch_course", text)
                queryset = Course.objects.filter(id=result)
            except ShnatonParserError as e:
                log.debug(e)
        result = [c.as_dict for c in queryset]
        result.sort(key=lambda c: c["score"], reverse=True)
        for course in result:
            course["url"] = reverse("course-details", args=[course["course_number"]])
            course["score"] = floatformat(course["score"])
        return JsonResponse({"courses": result})
