from django.db import models

from academic_helper.logic.shnaton_parser import ShnatonParser


class Course(models.Model):
    DELIMITER = ";"

    course_number = models.CharField(max_length=30, unique=True)
    name_he = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    year = models.IntegerField()
    semester = models.CharField(max_length=30)
    nz = models.IntegerField()


class CourseClass(models.Model):
    LEN_LONG = 300
    LEN_MEDIUM = 100
    LEN_SHORT = 30
    CLASS_TYPES = (
        ("lecture", "שיעור"),  # שעור
        ("recitation", "תרגיל"),  # תרג
        # שיעור ותרגיל
        ("seminar", "סמינריון"),  # סמ
        # שיעור וסמינריון
        ("guidance", "הדרכה"),  # הדר
        ("lab", "מעבדה"),  # מעב
        ("guidance and lecture", "שיעור ומעבדה"),  # שומ
        # שיעור והדרכה
        # סיור-מחנה
        ("preparatory", "מכינה"),  # מכי
        ("workshop", "סדנה"),  # סדנה
        ("practical work", "עבודה מעשית"),  # ע.מע
        # מחנה
        # שיעור וסדנה
        # שיעור תרגיל ומעבדה
        ("clinical", "שיעור קליני"),  # שק
        ("trip", "סיור"),  # סיור
        ("assignment", "מטלה"),  # מטלה
    )

    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_number = models.CharField(max_length=LEN_SHORT)
    serial_number = models.IntegerField()  # equiv of group
    lecturer = models.CharField(max_length=LEN_LONG)
    class_type = models.CharField(max_length=LEN_MEDIUM)
    group = models.CharField(max_length=LEN_SHORT)
    semester = models.CharField(max_length=LEN_MEDIUM)
    day = models.CharField(max_length=LEN_SHORT)
    hour = models.CharField(max_length=LEN_MEDIUM)
    hall = models.CharField(max_length=LEN_LONG)
