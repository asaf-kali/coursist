from star_ratings.models import AbstractBaseRating


class ExtendedRating(AbstractBaseRating):
    pass

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # bad = UserRating.objects.all().values("ip").annotate(total=Count("ip")).filter(total__gt=1).exists()
    # if bad:
    #     raise ValueError("Noooo")
    # super().save(force_insert, force_update, using, update_fields)
