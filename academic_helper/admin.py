from django.contrib import admin

from academic_helper.models import (
    StudyPlan,
    StudyBlock,
    CompletedCourse,
    ClassSchedule,
    Course,
    Faculty,
    CourseOccurrence,
    CourseClass,
    Campus,
    Hall,
    Teacher,
    ClassGroup,
    CoursistUser,
    RatingDummy,
    School,
)

admin.site.register(CoursistUser)
admin.site.register(Faculty)
admin.site.register(School)
admin.site.register(Course)
admin.site.register(CourseOccurrence)
admin.site.register(Campus)
admin.site.register(Hall)
admin.site.register(Teacher)
admin.site.register(ClassGroup)
admin.site.register(CourseClass)
admin.site.register(ClassSchedule)
admin.site.register(StudyBlock)
admin.site.register(CompletedCourse)
admin.site.register(RatingDummy)
admin.site.register(StudyPlan)
