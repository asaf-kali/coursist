from django.contrib.auth.models import AbstractUser

from academic_helper.models.base import Base


class ExtendedUser(AbstractUser, Base):
    pass
