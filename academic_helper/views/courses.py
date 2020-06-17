from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView

from academic_helper.models import Course
from academic_helper.utils.logger import log
from academic_helper.views.basic import ExtendedViewMixin


class CourseDetailsView(DetailView, ExtendedViewMixin):
    model = Course
    template_name = "courses/course-details.html"

    @property
    def title(self) -> str:
        return f"Course {self.object.course_number}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["semester_rating_description"] = "כמה קשה הקורס במהלך הסמסטר? כמה עמוסים שיעורי הבית? (1-קשה 5-קל)"
        context["semester_rating_title"] = "קושי במהלך הסמסטר"
        context["exams_rating_description"] = "כמה קשה הבחינה/פרוייקט גמר? (1-קשה 5-קל)"
        context["exams_rating_title"] = "בחינות"
        context["interest_rating_description"] = "כמה מעניין הקורס? כמה כיף? (1-לא מעניין 5-מעניין)"
        context["interest_rating_title"] = "עניין"
        return context

    @property
    def object(self):
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
        return Course.objects.all()[:50]

    def post(self, request: WSGIRequest):
        if not request.is_ajax():
            raise NotImplementedError()
        text = request.POST["free_text"]
        school = request.POST["school"]
        faculty = request.POST["faculty"]
        log.info(f"Searching for {text}, school {school}, faculty {faculty}...")
        queryset = Course.find_by(text, school, faculty)
        result = [c.as_dict for c in queryset]
        for course in result:
            course["url"] = reverse("course-details", args=[course["course_number"]])
        return JsonResponse({"courses": result})
