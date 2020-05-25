from django.contrib import admin

from academic_helper.models import StudyPlan
from academic_helper.models.course import Course, StudyBlock, CompletedCourse
from academic_helper.models.extended_rating import RatingDummy
from academic_helper.models.extended_user import ExtendedUser

admin.site.register(ExtendedUser)
admin.site.register(Course)
admin.site.register(RatingDummy)
admin.site.register(StudyBlock)
admin.site.register(CompletedCourse)
admin.site.register(StudyPlan)
