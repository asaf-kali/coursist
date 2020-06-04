import re

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic import TemplateView

from academic_helper.models import CoursistUser


def index(request):
    return render(request, "other/index.html")


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

    @property
    def user(self) -> CoursistUser:
        return self.request.user
