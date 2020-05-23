from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView

from reviews.models.course import Course


def index(request):
    return render(request, "index.html")


class ExtendedView(TemplateView):
    pass


class AjaxView(ExtendedView):
    template_name = "ajax.html"

    def get(self, request: WSGIRequest, *args, **kwargs):
        print("We are in GET")
        return super().get(request, *args, **kwargs)

    def post(self, request: WSGIRequest, *args, **kwargs):
        print("We are in POST")
        if request.is_ajax():
            value = "Hi " + request.POST["value"]
            print(f"User sent {value} via Ajax")
            return JsonResponse({"success": True, "value": value})
        else:
            value = request.POST["post-text"]
            print(f"User sent {value} via POST")
            return self.render_to_response(context={"value": value})


class CourseView(DetailView):
    model = Course
    template_name = "course-details.html"

    def get_object(self, queryset=None):
        return Course.objects.filter(course_number=self.kwargs["course_number"]).first()


class CoursesView(ListView, ExtendedView):
    model = Course
    template_name = "courses.html"

    @property
    def object_list(self):
        return Course.objects.all()
