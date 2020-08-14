from django.contrib import admin

from academic_helper.models import (
    DegreeProgram,
    StudyBlock,
    UserCourseChoice,
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
    Department,
    University,
)


class CoursistUserAdmin(admin.ModelAdmin):
    search_fields = ["pk", "username", "email", "first_name", "last_name"]
    list_display = ("username", "email", "date_joined")


admin.site.register(CoursistUser, CoursistUserAdmin)


class UniversityAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name", "abbreviation", "english_name"]
    list_display = ("id", "name", "abbreviation", "english_name")


admin.site.register(University, UniversityAdmin)


class FacultyAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name"]
    list_display = ("id", "name")


admin.site.register(Faculty, FacultyAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name", "faculty__name"]
    list_display = ("id", "name", "faculty")


admin.site.register(Department, DepartmentAdmin)


class CourseAdmin(admin.ModelAdmin):
    search_fields = ["pk", "course_number", "name"]
    list_display = ("course_number", "name")


admin.site.register(Course, CourseAdmin)


class CourseOccurrenceAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name", "course__course_number", "year", "semester"]
    list_display = ("id", "course_number", "name", "year", "semester")

    def course_number(self, obj: CourseOccurrence):
        return obj.course.course_number


admin.site.register(CourseOccurrence, CourseOccurrenceAdmin)


class CampusAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name"]
    list_display = ("id", "name")


admin.site.register(Campus, CampusAdmin)


class HallAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name", "campus__name"]
    list_display = ("id", "name", "campus")


admin.site.register(Hall, HallAdmin)


class TeacherAdmin(admin.ModelAdmin):
    search_fields = ["pk", "name"]
    list_display = ("id", "name")


admin.site.register(Teacher, TeacherAdmin)


class ClassGroupAdmin(admin.ModelAdmin):
    search_fields = ["pk", "mark", "occurrence__course__name", "class_type"]
    list_display = ("id", "mark", "course_name", "year", "semester", "class_type")
    filter_horizontal = ("teachers",)

    def course_name(self, obj: ClassGroup):
        return obj.occurrence.course.name


admin.site.register(ClassGroup, ClassGroupAdmin)


class CourseClassAdmin(admin.ModelAdmin):
    search_fields = ["teacher__name", "group__occurrence__course__name"]
    list_display = ("id", "course_name", "start_time", "end_time", "year", "semester", "group_mark", "teacher")

    def course_name(self, obj: CourseClass):
        return obj.group.occurrence.course.name

    def group_mark(self, obj: CourseClass):
        return obj.group.mark


admin.site.register(CourseClass, CourseClassAdmin)


class ClassScheduleAdmin(admin.ModelAdmin):
    search_fields = ["user__username", "group__occurrence__course__name"]
    list_display = ("id", "user", "group")


admin.site.register(ClassSchedule, ClassScheduleAdmin)


class StudyBlockAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("id", "name")
    filter_horizontal = ("courses",)


admin.site.register(StudyBlock, StudyBlockAdmin)


class CompletedCourseAdmin(admin.ModelAdmin):
    search_fields = ["course__name", "block__name", "user__username", "user__email"]
    list_display = ("id", "user", "block", "course")


admin.site.register(UserCourseChoice, CompletedCourseAdmin)


class DegreeProgramAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("id", "name")
    filter_horizontal = ("blocks",)


admin.site.register(DegreeProgram, DegreeProgramAdmin)


class RatingDummyAdmin(admin.ModelAdmin):
    search_fields = ["name", "object_id"]
    readonly_fields = ["content_object", "object_id"]
    list_display = ("id", "name", "content_object", "score")


admin.site.register(RatingDummy, RatingDummyAdmin)
