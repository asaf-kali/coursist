from rest_framework import serializers

from academic_helper.models.course import Course


class CourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    score = serializers.ReadOnlyField()

    class Meta:
        model = Course
        exclude = ["_name"]
        include = ["id"]