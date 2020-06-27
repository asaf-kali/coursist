from django.contrib import admin

from course_comments.models import CourseComment


class CourseCommentAdmin(admin.ModelAdmin):
    search_fields = ["pk", "user_name", "user_email", "comment"]


admin.site.register(CourseComment, CourseCommentAdmin)
