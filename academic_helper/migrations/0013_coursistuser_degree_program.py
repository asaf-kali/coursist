# Generated by Django 3.0.7 on 2020-08-13 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academic_helper", "0012_auto_20200710_1233"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursistuser",
            name="degree_program",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="academic_helper.DegreeProgram"
            ),
        ),
    ]
