from academic_helper.models import ClassSchedule
import arrow
from ics import Calendar, Event

# TODO: needs to be modeled in the DB
_HUJI_SEMESTER_DATES = {
    1: {"begin": arrow.get(year=2019, month=10, day=27), "end": arrow.get(year=2020, month=1, day=28),},
    2: {"begin": arrow.get(year=2020, month=3, day=12), "end": arrow.get(year=2020, month=6, day=30),},
}


class ScheduleExportError(Exception):
    pass


class ScheduleExport:
    def __init__(self, user):
        self.user = user

    def get_user_choices_as_events(self):
        schedules = ClassSchedule.objects.filter(user=self.user)
        data = []
        for schedule_event in schedules:
            course_name = schedule_event.group.occurrence.course.name
            course_year = schedule_event.group.occurrence.year
            course_number = schedule_event.group.occurrence.course.course_number
            for event in schedule_event.group.courseclass_set.all():
                data.append(
                    dict(
                        course_name=course_name,
                        course_number=course_number,
                        hall_name=event.hall.name,
                        campus=event.hall.campus.name,
                        department=schedule_event.group.occurrence.course.department.name,
                        semester=event.semester,
                        day=event.day,
                        start_time=event.start_time,
                        end_time=event.end_time,
                        course_year=course_year,
                    )
                )
        return data

    def as_dict(self):
        return self.get_user_choices_as_events()

    def as_ical(self):
        courses = self.get_user_choices_as_events()
        events = self._get_ical_events(courses)
        calendar = Calendar(events=events)
        return calendar

    def _get_ical_events(self, courses):
        events = []
        for course in courses:
            time_range = self._get_all_events_for_course(course)
            for event_begin in time_range:
                event = Event()
                event.name = course["course_name"]
                event.begin = event_begin
                event.end = event_begin.replace(
                    hour=course["end_time"].hour,
                    minute=course["end_time"].minute,
                    second=0,
                    year=course["course_year"],
                )
                event.location = f"{course['hall_name']}, {course['campus']}"
                events.append(event)
        return events

    def _get_all_events_for_course(self, course):
        if course["semester"] not in _HUJI_SEMESTER_DATES:
            raise ScheduleExportError(f'Unknown Semester encoding: {course["semester"]}')

        semester_begin = _HUJI_SEMESTER_DATES[course["semester"]]["begin"]
        semester_end = _HUJI_SEMESTER_DATES[course["semester"]]["end"]

        course_begin = self._calculate_course_first_day(
            semester_begin, course["day"], course["start_time"].hour, course["start_time"].minute,
        )
        events = self._calculate_weekly_events(course_begin, semester_end)

        return events

    def _calculate_course_first_day(self, begin_date, event_day, event_hour, event_minute):
        return begin_date.shift(weekday=(event_day - 2) % 7).replace(hour=event_hour, minute=event_minute, second=0)

    def _calculate_weekly_events(self, begin_date, end_date):
        if end_date <= begin_date:
            raise ScheduleExportError(
                f"Begin date must be smaller than End date: begin_date={begin_date}, end_date={end_date}"
            )
        dates = []
        current = begin_date
        while current <= end_date:
            dates.append(current)
            current = current.shift(weeks=1)
        return dates
