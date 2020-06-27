import re

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.views.generic import TemplateView
from academic_helper.models import CoursistUser
from django.shortcuts import redirect

from academic_helper.utils.logger import log, wrap


class IndexView(TemplateView):
    template_name = "other/index.html"


def redirect_to_courses_view(request):
    response = redirect("courses")
    return response


class ExtendedViewMixin(PermissionRequiredMixin, TemplateView):
    @property
    def title(self) -> str:
        base_name = self.__class__.__name__
        base_name = base_name.replace("View", "")
        return re.sub(r"(.)([A-Z])", "\\1 \\2", base_name)

    def get_context_data(self, **kwargs):
        log.info(f"Rendering {wrap(self.title)} for {wrap(self.user)}")
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        pass

    @property
    def user(self) -> CoursistUser:
        return self.request.user

    @property
    def object(self):
        """ This is a useful patch for some views. """
        return self.get_object()

    def has_permission(self):
        return True
