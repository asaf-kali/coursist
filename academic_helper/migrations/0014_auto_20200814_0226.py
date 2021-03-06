# Generated by Django 3.0.7 on 2020-08-13 23:26

import django.db.models.deletion
from django.db import migrations, models


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
            options={
                "abstract": False,
            },
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
        migrations.AlterUniqueTogether(
            name="course",
            unique_together={("course_number", "university")},
        ),
    ]
