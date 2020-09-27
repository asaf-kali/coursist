from dataclasses import dataclass

from academic_helper.utils.logger import wrap


class CoursistError(Exception):
    pass


class UserNotLoggedInError(CoursistError):
    pass


@dataclass
class CourseNotFoundError(CoursistError):
    course_number: str

    def __post_init__(self):
        super(f"Course number {wrap(self.course_number)} was not found")


class ShnatonParserError(CoursistError):
    pass


class FetchRawDataError(ShnatonParserError):
    pass


class HtmlFormatError(ShnatonParserError):
    pass
