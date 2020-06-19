from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.urls import reverse

from academic_helper.utils.logger import log
from academic_helper.views.basic import ExtendedViewMixin


class AboutView(ExtendedViewMixin):
    template_name = "other/about.html"


class AjaxView(ExtendedViewMixin):
    template_name = "other/ajax.html"

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
