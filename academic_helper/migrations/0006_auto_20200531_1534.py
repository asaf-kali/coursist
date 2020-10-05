# Generated by Django 3.0.6 on 2020-05-31 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academic_helper", "0005_auto_20200530_2121"),
    ]

    operations = [
        migrations.AlterField(
            model_name="classgroup",
            name="class_type",
            field=models.IntegerField(
                choices=[
                    (1, "Lecture"),
                    (2, "Recitation"),
                    (3, "Seminar"),
                    (4, "Lab"),
                    (5, "Workshop"),
                    (6, "Assignment"),
                    (7, "Clinical"),
                    (8, "Trip"),
                    (9, "Preparatory"),
                    (10, "Guidance"),
                    (11, "Lesson And Lab"),
                    (12, "Shut"),
                    (13, "Practical Work"),
                    (14, "Lesson And Workshop"),
                    (15, "Lesson And Guidance"),
                    (16, "Lesson And Seminar"),
                    (17, "Camp"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="courseclass",
            name="day",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (-1, "Undefined"),
                    (1, "Sunday"),
                    (2, "Monday"),
                    (3, "Tuesday"),
                    (4, "Wednesday"),
                    (5, "Thursday"),
                    (6, "Friday"),
                    (7, "Saturday"),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="courseclass", name="end_time", field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="courseclass", name="start_time", field=models.TimeField(blank=True, null=True),
        ),
    ]