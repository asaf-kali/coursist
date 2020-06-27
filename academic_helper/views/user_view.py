from functools import lru_cache

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.detail import SingleObjectMixin

from academic_helper.models import CoursistUser
from academic_helper.utils.tools import parse_bool
from academic_helper.views.basic import ExtendedViewMixin
from course_comments.models import CourseComment


class UserView(ExtendedViewMixin, SingleObjectMixin):
    model = CoursistUser
    template_name = "user/user.html"

    @property
    def title(self) -> str:
        return f"Coursist - {self.object.username}"

    def has_permission(self):
        return self.user.pk == self.object.pk or self.user.has_perm(CoursistUser.permissions.view)

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["user_details"] = self.object
        result["comments"] = CourseComment.for_user(self.object.pk)
        return result

    @lru_cache(maxsize=1)  # TODO: Think good about this, can cause horrible bugs
    def get_object(self, queryset=None):
        queryset = CoursistUser.objects.filter(username=self.kwargs["username"])
        return get_object_or_404(queryset)

    def on_anonymous_change(self):
        try:
            comment_id = self.request.POST["comment_id"]
            is_anonymous = parse_bool(self.request.POST["is_anonymous"])
        except (KeyError, ValueError) as e:
            return HttpResponse(content=str(e), status=400)
        CourseComment.set_anonymous(comment_id, is_anonymous)
        return HttpResponse("Approval saved", status=200)

    def post(self, request: WSGIRequest, **kwargs):
        if request.is_ajax():
            return self.on_anonymous_change()
        return HttpResponse(status=400)
