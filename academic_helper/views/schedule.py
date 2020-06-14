import json

from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest

from academic_helper.logic.errors import UserNotLoggedInError, CourseNotFoundError
from academic_helper.logic.schedule import set_user_schedule_group, \
    get_user_choices, get_all_classes, get_courses_by_groups
from academic_helper.models.course import Course
from academic_helper.views.basic import ExtendedViewMixin


class ScheduleView(ExtendedViewMixin):
    template_name = "schedule/schedule.html"

    @property
    def title(self) -> str:
        return "Schedule Planner"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["choices"] = get_user_choices(self.user)
        return context

    def search(self, search_val: str):
        courses = Course.objects.filter(
            Q(name__icontains=search_val) | Q(course_number__icontains=search_val)
        ).order_by("course_number")[:10]
        serialized = [c.as_dict for c in courses]
        return JsonResponse({"status": "success", "courses": serialized}, json_dumps_params={"ensure_ascii": False})

    def get_classes(self, course_number):
        if not course_number.isdigit():
            return HttpResponseBadRequest()
        try:
            groups = get_all_classes(course_number)
            return JsonResponse({"status": "success", "groups": groups})
        except CourseNotFoundError as e:
            return JsonResponse({"status": "error", "message": "Course not found"})

    def on_user_group_choice(self, choice):
        try:
            set_user_schedule_group(self.user, choice)
        except UserNotLoggedInError:
            return JsonResponse({"status": "error", "message": "User not logged in"})
        return JsonResponse({"status": "success"})

    def get_courses_by_groups(self, groups):
        courses = get_courses_by_groups(groups)
        return JsonResponse({"status": "success", "courses": courses},
                            json_dumps_params={"ensure_ascii": False})

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return
        if "search_val" in request.POST:
            search_val = request.POST["search_val"]
            return self.search(search_val)
        if "course_number" in request.POST:
            course_number = request.POST["course_number"]
            return self.get_classes(course_number)
        if "group_choice" in request.POST:
            choice = request.POST["group_choice"]
            return self.on_user_group_choice(choice)
        if "groups":
            groups = json.loads(request.POST["groups"])['groups']
            return self.get_courses_by_groups(groups)
        else:
            return HttpResponseBadRequest()
