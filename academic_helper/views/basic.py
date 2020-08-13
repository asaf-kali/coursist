import json
import re
from dataclasses import dataclass
from enum import Enum

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.views.generic import TemplateView

from academic_helper.models import CoursistUser, NOT_SELECTED
from academic_helper.utils.logger import log, wrap


class IndexView(TemplateView):
    template_name = "other/index.html"


def redirect_to_courses_view(request):
    response = redirect("courses")
    return response


class ToastTag(Enum):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Toast:
    text: str
    title: str = ""
    delay: int = 5000
    tag: ToastTag = ToastTag.INFO

    def as_json(self):
        as_dict = self.__dict__
        as_dict["tag"] = self.tag.value
        return json.dumps(as_dict)


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
        context["not_selected"] = NOT_SELECTED
        # context["toasts"] = [
        #     Toast("משהו טוב קרה", delay=2500).as_json(),
        #     Toast("משהו לא טוב קרה", delay=3000, tag=ToastTag.WARNING).as_json(), ]
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
