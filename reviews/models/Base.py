from django.db.models import Model, AutoField


class Base(Model):
    id: int = AutoField(primary_key=True, editable=False)

    class Meta:
        abstract = True
