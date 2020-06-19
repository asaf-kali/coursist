from academic_helper.models import Semester, CourseClass, List


def find_common_semester(classes: List[CourseClass]) -> int:
    result = None
    for cls in classes:
        if result is None:
            result = cls.semester
        elif result != cls.semester:
            return Semester.YEARLY.value
    return result
