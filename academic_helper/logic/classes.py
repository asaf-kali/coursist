from typing import List

from academic_helper.models.course_occurrence import CourseClass, Semester


def find_common_semester(classes: List[CourseClass]) -> int:
    result = None
    for cls in classes:
        if result is None:
            result = cls.semester
        elif result != cls.semester:
            return Semester.YEARLY.value
    return result
