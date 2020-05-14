from django.contrib.auth.models import AbstractUser

from reviews.models.base import Base


class ExtendedUser(AbstractUser, Base):
    pass
