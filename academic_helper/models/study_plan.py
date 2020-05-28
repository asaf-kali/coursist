from django.db import models

from academic_helper.models import Base
from academic_helper.models.course import StudyBlock


class StudyPlan(Base):
    name: str = models.CharField(max_length=50)
    blocks = models.ManyToManyField(StudyBlock)
    credits: int = models.IntegerField()
    is_public: bool = models.BooleanField(default=True)

    def __str__(self):
        return f"Plan {self.id} - {self.name}"
