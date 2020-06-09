from academic_helper.models.degree_program import *
from academic_helper.views.basic import ExtendedViewMixin


# class AllDegreePrograms(ExtendedViewMixin):
#     model = DegreeProgram
#     template_name = "degree_programs/all_study_plans.html"
#
#     @property
#     def title(self) -> str:
#         return "All Study Plans Beta"


class UserDegreeProgram(ExtendedViewMixin):
    model = DegreeProgram
    template_name = "degree_programs/user_degree_plan.html"

    @property
    def title(self) -> str:
        return "My Degree Program - Beta"
