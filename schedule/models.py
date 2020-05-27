from django.db import models

from schedule.shnaton_parser import ShnatonParser


class Course(models.Model):
    DELIMITER = ';'
    LEN_LONG = 300
    LEN_MEDIUM = 100
    LEN_SHORT = 30
    COURSE_SEMESTER = (
        ('A', "א'"),
        ('B', "ב'"),
        ('AB', "א' ו\או ב'"),
        ('YEAR', 'שנתי'),
        ('SUMMER', 'קיץ'),
    )

    course_number = models.CharField(max_length=LEN_SHORT, unique=True)
    name_he = models.CharField(max_length=LEN_LONG)
    name_en = models.CharField(max_length=LEN_LONG)
    year = models.IntegerField()
    semester = models.CharField(max_length=LEN_SHORT)
    nz = models.IntegerField()

    @staticmethod
    def fetch_course(course_number):
        """
        Fetch course from Shnaton, add it to the database and return it.
        :param course_number: The course number to search.
        :return: The course model object of the fetched course and its classes,
         or None if the course wasn't found.
        """
        if not course_number.isdigit():
            return None

        # TODO make year 2020 a variable
        parsed_course = ShnatonParser.parse_course('2020', course_number)
        if parsed_course is None:
            return None

        new_course = Course()
        new_course.course_number = parsed_course['id']
        new_course.name_he = parsed_course['name']
        new_course.year = parsed_course['year']
        new_course.semester = parsed_course['semester']
        new_course.nz = parsed_course['nz']
        new_course.save()

        result = Course.objects.filter(course_number__exact=course_number)

        # TODO need to add also the classes of the course
        print(parsed_course['lessons'])
        serial_num = 0
        for lesson in parsed_course['lessons']:
            # prepare values to insert
            lecturer = Course.DELIMITER.join(lesson['lecturer'])
            class_type = lesson['type']
            group = lesson['group']
            semester = Course.DELIMITER.join(lesson['semester'])
            day = Course.DELIMITER.join(lesson['day'])
            hour = Course.DELIMITER.join(lesson['hour'])
            hall = Course.DELIMITER.join(lesson['hall'])

            # create new class and save
            new_class = CourseClass()
            new_class.course_id = new_course
            new_class.course_number = new_course.course_number
            new_class.serial_number = serial_num
            serial_num += 1
            new_class.lecturer = lecturer
            new_class.class_type = class_type
            new_class.group = group
            new_class.semester = semester
            new_class.day = day
            new_class.hour = hour
            new_class.hall = hall
            new_class.save()

        return result


class CourseClass(models.Model):
    LEN_LONG = 300
    LEN_MEDIUM = 100
    LEN_SHORT = 30
    CLASS_TYPES = (
        ('lecture', 'שיעור'), # שעור
        ('recitation', 'תרגיל'), # תרג
        # שיעור ותרגיל
        ('seminar', 'סמינריון'), # סמ
        # שיעור וסמינריון
        ('guidance', 'הדרכה'), # הדר
        ('lab', 'מעבדה'), # מעב
        ('guidance and lecture', 'שיעור ומעבדה'), # שומ
        # שיעור והדרכה
        # סיור-מחנה
        ('preparatory', 'מכינה'), # מכי
        ('workshop', 'סדנה'), # סדנה
        ('practical work', 'עבודה מעשית'), # ע.מע
        # מחנה
        # שיעור וסדנה
        # שיעור תרגיל ומעבדה
        ('clinical', 'שיעור קליני'), # שק
        ('trip', 'סיור'), # סיור
        ('assignment', 'מטלה') # מטלה
    )
    CLASS_SEMESTER = (
        ('A', "א'"),
        ('B', "ב'"),
        ('YEAR', 'שנתי'),
        ('SUMMER', 'קיץ'),
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
