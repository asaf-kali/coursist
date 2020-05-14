from django.contrib import admin

from reviews.models.extended_user import ExtendedUser
from reviews.models.course import Course

admin.site.register(ExtendedUser)
admin.site.register(Course)
