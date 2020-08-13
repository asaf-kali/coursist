from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator

from academic_helper.models import NOT_SELECTED
from academic_helper.models.degree_program import *
from academic_helper.views.basic import ExtendedViewMixin


# class AllDegreePrograms(ExtendedViewMixin):
#     model = DegreeProgram
#     template_name = "degree_programs/all_study_plans.html"
#
#     @property
#     def title(self) -> str:
#         return "All Study Plans Beta"


@method_decorator(login_required, name="dispatch")
class UserDegreeProgram(ExtendedViewMixin):
    model = DegreeProgram
    template_name = "degree_programs/my_degree_plan.html"

    @property
    def title(self) -> str:
        return "My Degree Program"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_program"] = self.user.degree_program
        context["degree_programs"] = DegreeProgram.public_programs()
        context["queue_block"] = {"name": "מאגר חופשי", "id": NOT_SELECTED}
        return context

    def on_program_choice(self, program_id):
        program_id = int(program_id)
        if program_id == NOT_SELECTED:
            program_id = None
        self.user.set_degree_program(program_id)
        return JsonResponse(data={"user": self.user.id, "program_id": program_id}, status=200)

    def on_move_course(self, course_id, block_id):
        UserCourseChoice.move_course(self.user.id, course_id, block_id)
        return HttpResponse(200)

    def post(self, request: WSGIRequest, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponse(status=400)
        if "action" not in request.POST:
            return HttpResponse(status=400)
        action = request.POST["action"]
        if action == "change_program":
            return self.on_program_choice(request.POST["program_id"])
        if action == "move_course":
            return self.on_move_course(request.POST["course_id"], request.POST["block_id"])
        return HttpResponse(status=400)
