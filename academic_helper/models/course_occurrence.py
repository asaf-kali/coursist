from datetime import time, date

from django.db import models

from academic_helper.models.base import Base, ChoicesEnum
from academic_helper.models.course import Course


class Semester(ChoicesEnum):
    A = 1
    B = 2
    C = 3
    SUMMER = 4
    YEARLY = 5


class ClassType(ChoicesEnum):
    LECTURE = 1  # שעור
    RECITATION = 2  # תרג
    SEMINAR = 3  # סמ
    LAB = 4  # מעב
    WORKSHOP = 5
    ASSIGNMENT = 6  # מטלה
    CLINICAL = 7  # שק
    TRIP = 8  # סיור
    PREPARATORY = 9  # מכי
    GUIDANCE = 10  # הדר
    LESSON_AND_LAB = 11  # שומ
    SHUT = 12  # שות
    PRACTICAL_WORK = 13  # ע.מע
    LESSON_AND_WORKSHOP = 14  # שוסד
    LESSON_AND_GUIDANCE = 15  # שוה
    LESSON_AND_SEMINAR = 16  # שוס
    CAMP = 17  # מחנה


class DayOfWeek(ChoicesEnum):
    UNDEFINED = -1
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7


SEMESTER_NAMES = {
    Semester.A.value: "א'",
    Semester.B.value: "ב'",
    Semester.C.value: "ג'",
    Semester.SUMMER.value: "קיץ",
    Semester.YEARLY.value: "שנתי",
}


class CourseOccurrence(Base):
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name: str = models.CharField(max_length=150, default="-")
    year: int = models.IntegerField()
    semester: int = models.IntegerField(choices=Semester.list())
    credits: int = models.IntegerField()
    notes: str = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["course__course_number", "year", "semester"]
        unique_together = ["course", "year", "semester"]

    def __str__(self):
        return f"{self.course} | {self.year} {SEMESTER_NAMES[self.semester]}"

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    @staticmethod
    def get_latest_course_name(course_number) -> str:
        occurrences = CourseOccurrence.objects.filter(course__course_number=course_number)
        if not occurrences.exists():
            return "לא זמין"
        return occurrences.last().name


class Campus(Base):
    name: str = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "campuses"

    def __str__(self):
        return self.name


class Hall(Base):
    name: str = models.CharField(max_length=100)
    campus: Campus = models.ForeignKey(Campus, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.campus is not None and isinstance(self.campus, str):
            self.campus = Campus.objects.get_or_create(name=self.campus)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{f'{self.campus} | ' if self.campus else ''}{self.name}"


class Teacher(Base):
    name: str = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = " ".join(self.name.strip().split())
        super().save(*args, **kwargs)


class ClassGroup(Base):
    occurrence = models.ForeignKey(CourseOccurrence, on_delete=models.CASCADE)
    class_type = models.IntegerField(choices=ClassType.list())
    mark = models.CharField(max_length=30, null=True, blank=True)
    teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return f"{self.occurrence} | {ClassType(self.class_type).readable_name} | {self.mark}"

    class Meta:
        unique_together = ["occurrence", "class_type", "mark"]

    @property
    def as_dict(self) -> dict:
        result = super().as_dict
        result["teachers"] = [str(teacher) for teacher in self.teachers.all()]
        return result

    @property
    def year(self) -> int:
        return self.occurrence.year

    @property
    def semester(self) -> int:
        return self.occurrence.semester


class CourseClass(Base):
    group: ClassGroup = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    teacher: Teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    semester: int = models.IntegerField(choices=Semester.list(), null=True, blank=True)
    day: int = models.IntegerField(choices=DayOfWeek.list(), null=True, blank=True)
    start_time: time = models.TimeField(null=True, blank=True)
    end_time: time = models.TimeField(null=True, blank=True)
    hall: Hall = models.ForeignKey(Hall, on_delete=models.SET_NULL, null=True, blank=True)
    special_occurrence: date = models.DateField(null=True, blank=True)
    notes: str = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = "course classes"

    @property
    def as_dict(self) -> dict:
        result = super().as_dict
        result["teacher"] = str(self.teacher)
        result["hall"] = str(self.hall)
        return result

    @property
    def year(self) -> int:
        return self.group.year

    def __str__(self):
        return f"{self.group} - {DayOfWeek(self.day).readable_name} {self.hall}"
