# Generated by Django 3.0.6 on 2020-05-25 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("academic_helper", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RatingDummy",
            fields=[
                ("id", models.AutoField(editable=False, primary_key=True, serialize=False)),
                ("object_id", models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ("name", models.CharField(max_length=50)),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
