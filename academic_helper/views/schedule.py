import json
from io import BytesIO
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.http import FileResponse
from django.core.serializers.json import DjangoJSONEncoder
from academic_helper.logic.errors import UserNotLoggedInError, CourseNotFoundError
from academic_helper.logic.schedule import (
    set_user_schedule_group,
    get_user_choices,
    get_all_classes,
    del_user_schedule_groups,
)

from academic_helper.logic.schedule_export import ScheduleExport
from academic_helper.models.course import Course
from academic_helper.views.basic import ExtendedViewMixin
import logging
import arrow

LOG = logging.getLogger(__name__)
SCHEDULE_COOKIE = "schedule"


class ScheduleView(ExtendedViewMixin):
    template_name = "schedule/schedule.html"

    @property
    def title(self) -> str:
        return "Schedule Planner"

    def get(self, request, *args, **kwargs):
        if request.GET.get("download") == "ical":
            ical = ScheduleExport(user=self.user).as_ical()
            buffer = BytesIO()
            buffer.writelines([line.encode() for line in ical])
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=f"coursist_export_{self.user}_{arrow.utcnow()}.ics",
            )
        elif request.GET.get("download") == "json":
            event_json = ScheduleExport(user=self.user).as_dict()
            buffer = BytesIO()
            buffer.write(json.dumps(event_json, indent=4, sort_keys=True, cls=DjangoJSONEncoder).encode())
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=f"coursist_export_{self.user}_{arrow.utcnow()}.json",
            )
        else:
            response = super().get(request, *args, **kwargs)
            if self.user.is_authenticated and SCHEDULE_COOKIE in self.request.COOKIES:
                # safe to delete the cookie here, because super has already called
                # get_context_data, which already used this cookie
                response.delete_cookie(SCHEDULE_COOKIE)
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cookie_choices = []
        if SCHEDULE_COOKIE in self.request.COOKIES:
            cookie_choices = json.loads(self.request.COOKIES[SCHEDULE_COOKIE])
            cookie_choices = cookie_choices["groups"]

        context["choices"] = get_user_choices(self.user, cookie_choices)
        context["logged_in"] = self.user.is_authenticated

        return context

    def on_search_course(self, search_val: str):
        courses = Course.objects.filter(
            Q(name__icontains=search_val) | Q(course_number__icontains=search_val)
        ).order_by("course_number")[:10]
        serialized = [c.as_dict for c in courses]
        return JsonResponse({"status": "success", "courses": serialized}, json_dumps_params={"ensure_ascii": False},)

    def get_classes(self, course_number):
        if not course_number.isdigit():
            return HttpResponseBadRequest()
        try:
            groups = get_all_classes(course_number)
            return JsonResponse({"status": "success", "groups": groups})
        except CourseNotFoundError:
            return JsonResponse({"status": "error", "message": "Course not found"})

    def on_user_group_choice(self, choice):
        try:
            set_user_schedule_group(self.user, choice)
        except UserNotLoggedInError:
            return JsonResponse({"status": "error", "message": "User not logged in"})
        return JsonResponse({"status": "success"})

    def on_user_delete_groups(self, choices):
        try:
            del_user_schedule_groups(self.user, choices)
        except UserNotLoggedInError:
            return JsonResponse({"status": "error", "message": "User not logged in"})
        return JsonResponse({"status": "success"})

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return
        if "search_val" in request.POST:
            search_val = request.POST["search_val"]
            return self.on_search_course(search_val)
        elif "course_number" in request.POST:
            course_number = request.POST["course_number"]
            return self.get_classes(course_number)
        elif "group_choice" in request.POST:
            choice = request.POST["group_choice"]
            return self.on_user_group_choice(choice)
        elif "groups_to_del" in request.POST:
            choices = json.loads(request.POST["groups_to_del"])["group_ids"]
            return self.on_user_delete_groups(choices)
        else:
            return HttpResponseBadRequest()
