from django.contrib import admin

from academic_helper.models import StudyPlan, StudyBlock, CompletedCourse
from academic_helper.models.course import Course, Faculty
from academic_helper.models.course_occurrence import CourseOccurrence, CourseClass
from academic_helper.models.extended_rating import RatingDummy
from academic_helper.models.extended_user import ExtendedUser

admin.site.register(ExtendedUser)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(CourseOccurrence)
admin.site.register(CourseClass)
admin.site.register(StudyBlock)
admin.site.register(CompletedCourse)
admin.site.register(RatingDummy)
admin.site.register(StudyPlan)
