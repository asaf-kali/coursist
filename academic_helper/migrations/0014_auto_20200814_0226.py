# Generated by Django 3.0.7 on 2020-08-13 23:26

import django.db.models.deletion
from django.db import migrations, models

from academic_helper.models import University, Course, Faculty
from academic_helper.utils.logger import log, wrap


def handle_uni_default(apps, schema_editor):
    log.info(f"Creating default university")
    def_uni = University(name="Default university", english_name="Default university", abbreviation="DU")
    def_uni.save()
    for course in Course.objects.all():
        if not course.university:
            log.info(f"Changing university for course {wrap(course.id)}")
            course.university = def_uni
            course.save()
        else:
            log.info(f"Course {wrap(course.id)} already had university: ${wrap(course.university)}")
    for faculty in Faculty.objects.all():
        if not faculty.university:
            log.info(f"Changing university for faculty {wrap(faculty.id)}")
            faculty.university = def_uni
            faculty.save()
        else:
            log.info(f"Faculty {wrap(faculty.id)} already had university: ${wrap(faculty.university)}")


class Migration(migrations.Migration):
    dependencies = [
        ("academic_helper", "0013_coursistuser_degree_program"),
    ]

    operations = [
        migrations.CreateModel(
            name="University",
            fields=[
                ("id", models.AutoField(editable=False, primary_key=True, serialize=False)),
                ("abbreviation", models.CharField(max_length=10)),
                ("name", models.CharField(max_length=150)),
                ("english_name", models.CharField(max_length=150)),
            ],
            options={"abstract": False,},
        ),
        migrations.AlterField(
            model_name="usercoursechoice",
            name="block",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="academic_helper.StudyBlock"
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="university",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="academic_helper.University"
            ),
        ),
        migrations.AddField(
            model_name="faculty",
            name="university",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="academic_helper.University"
            ),
        ),
        migrations.AlterUniqueTogether(name="course", unique_together={("course_number", "university")},),
        migrations.RunPython(handle_uni_default),
    ]
