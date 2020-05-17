from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from reviews.models.course import Course


# def index(request):
#     all_courses = Course.all_courses()
#     return render(request, "index.html", context={"courses": all_courses, "my_number": 8, "now": timezone.now()})


class IndexView(TemplateView):
    template_name = "index.html"

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
    template_name = "course-view.html"
