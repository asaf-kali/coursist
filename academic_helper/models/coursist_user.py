from django.contrib.auth.models import AbstractUser

from academic_helper.models.base import Base
from academic_helper.utils.logger import log, wrap


class CoursistUser(AbstractUser, Base):
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        log.info(f"Saving user: {wrap(self)}")
