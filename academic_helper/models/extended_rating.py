from django.contrib.admin.options import get_content_type_for_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from star_ratings.models import AbstractBaseRating

from academic_helper.models import Base


class ExtendedRating(AbstractBaseRating):
    pass


class RatingDummy(Base):
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey()
    name: str = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} rating for {self.content_object}"

    @staticmethod
    def dummy_for(obj, name: str) -> "RatingDummy":
        content_type = get_content_type_for_model(obj)
        return RatingDummy.objects.get_or_create(content_type=content_type, object_id=obj.id, name=name)[0]
