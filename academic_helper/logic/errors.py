from dataclasses import dataclass

from academic_helper.utils.logger import wrap


class UserNotLoggedInError(Exception):
    pass


@dataclass
class CourseNotFoundError(Exception):
    course_number: str

    def __post_init__(self):
        super(f"Course number {wrap(self.course_number)} was not found")
