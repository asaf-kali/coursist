from django.db.models import CharField, ManyToManyField, BooleanField, IntegerField

from academic_helper.models import Base
from academic_helper.models.course import StudyBlock


class StudyPlan(Base):
    name: str = CharField(max_length=50)
    blocks = ManyToManyField(StudyBlock)
    credits: int = IntegerField()
    is_public: bool = BooleanField(default=True)

    def __str__(self):
        return f"Plan {self.id} - {self.name}"
