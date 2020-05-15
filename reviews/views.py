from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from reviews.models.course import Course


def index(request):
    all_courses = Course.all_courses()
    return render(request, "index.html", context={"courses": all_courses, "my_number": 8, "now": timezone.now()})


class IndexView(TemplateView):
    template_name = "index.html"

    def post(self, request: WSGIRequest, *args, **kwargs):
        if request.is_ajax():
            return JsonResponse({"success": True, "value": request.POST["value"]})
        else:
            return self.render_to_response(context={"value": request.POST["post-text"]})
