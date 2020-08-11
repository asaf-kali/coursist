from typing import List, Iterable

from academic_helper.logic.classes import find_common_semester
from academic_helper.logic.errors import UserNotLoggedInError, CourseNotFoundError
from academic_helper.models import ClassGroup, ClassSchedule, Course, CourseClass
from academic_helper.utils.logger import wrap, log

CURRENT_YEAR = 2021


def get_user_choices(user, cookie_choices: Iterable, year: int = CURRENT_YEAR) -> dict:
    if user.is_anonymous:
        groups = [group for group in ClassGroup.objects.filter(id__in=cookie_choices)]
    else:
        if cookie_choices:
            import_from_cookies(user, cookie_choices)
        user_choices = ClassSchedule.objects.filter(user=user, group__occurrence__year=year)
        groups = [choice.group for choice in user_choices]

    choices = {"courses": [], "group_ids": []}
    added_courses = set()
    for group in groups:
        cur_course = group.occurrence.course
        if cur_course.course_number not in added_courses:
            added_courses.add(cur_course.course_number)
            choices["courses"].append(cur_course.as_dict)
        choices["group_ids"].append(group.id)

    return choices


def import_from_cookies(user, cookie_choices):
    for group_id in cookie_choices:
        try:
            set_user_schedule_group(user, group_id)
        except ClassGroup.DoesNotExist:
            pass


def set_user_schedule_group(user, group_id):
    log.info(f"set_user_schedule_group for user {wrap(user)} with group_id {wrap(group_id)}")
    if user.is_anonymous:
        # log.warning("set_user_schedule_group called but user is_anonymous")
        raise UserNotLoggedInError()
    group = ClassGroup.objects.get(pk=group_id)
    existing = ClassSchedule.objects.filter(
        user=user, group__occurrence__course=group.occurrence.course, group__class_type=group.class_type
    ).first()
    if existing:
        log.info(f"set_user_schedule_group replacing existing {wrap(existing.group.id)}")
        existing.delete()
    schedule = ClassSchedule(user=user, group=group)
    schedule.save()
    log.info(f"set_user_schedule_group added {wrap(group.id)}")


def del_user_schedule_groups(user, group_ids):
    log.info(f"del_user_schedule_group for user {wrap(user)} with group_ids {wrap(group_ids)}")
    if user.is_anonymous:
        log.warning("del_user_schedule_group called but user is_anonymous")
        raise UserNotLoggedInError()
    ClassSchedule.objects.filter(user=user, group_id__in=group_ids).delete()
    log.info(f"del_user_schedule_group deleted {wrap(group_ids)}")


def get_all_classes(course_number: str, year: int = None) -> List[dict]:
    if not year:
        year = CURRENT_YEAR
    course = Course.objects.filter(course_number=course_number).last()
    if not course:
        raise CourseNotFoundError(course_number)
    all_classes = CourseClass.objects.filter(
        group__occurrence__course=course, group__occurrence__year=year
    ).select_related("group")
    groups = list(set(c.group for c in all_classes))
    groups = sorted(groups, key=lambda g: g.mark)
    serialized = [g.as_dict for g in groups]
    for group in serialized:
        classes = [c for c in all_classes if c.group_id == group["id"]]
        group["classes"] = [c.as_dict for c in classes]
        group["semester"] = find_common_semester(classes)
    return serialized
