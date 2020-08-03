from typing import Optional, List, Collection, Union

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from star_ratings.models import AbstractBaseRating, UserRating, Rating

from academic_helper.models import Base


class ExtendedRating(AbstractBaseRating):
    pass


class RatingDummy(Base):
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey()
    name: str = models.CharField(max_length=50)

    class Meta:
        unique_together = ["content_type", "object_id", "name"]

    def __str__(self):
        return f"{self.name} rating for {self.content_object}"

    @staticmethod
    def dummy_for(obj, name: str) -> "RatingDummy":
        content_type = get_content_type_for_model(obj)
        return RatingDummy.objects.get_or_create(content_type=content_type, object_id=obj.id, name=name)[0]

    @staticmethod
    def dummies_for(obj, names: Collection[str]) -> Union[QuerySet, List["RatingDummy"]]:
        content_type = get_content_type_for_model(obj)
        return RatingDummy.objects.filter(content_type=content_type, object_id=obj.id, name__in=names)

    @property
    def score(self) -> float:
        rating = Rating.objects.filter(object_id=self.id, content_type__model="ratingdummy").first()
        if not rating:
            return 0
        return rating.average

    def get_user_rating(self, user) -> Optional[UserRating]:
        semester_rating = UserRating.objects.filter(user=user, rating__object_id=self.id)
        if len(semester_rating) == 1:
            return semester_rating[0]
        return None
