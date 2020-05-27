import json
from dataclasses import dataclass
from typing import KeysView, List

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, AutoField, Manager
from django.forms import model_to_dict
from django.utils.decorators import classproperty

from academic_helper.utils.logger import log, wrap


@dataclass
class Permissions:
    _app_name: str
    _obj_name: str

    def _get_permission(self, name: str) -> str:
        return f"{self.app_name}.{name}{self._obj_name}"

    @property
    def view(self) -> str:
        return self._get_permission("view")

    @property
    def add(self) -> str:
        return self._get_permission("add")

    @property
    def change(self) -> str:
        return self._get_permission("change")

    @property
    def delete(self) -> str:
        return self._get_permission("property")

    @property
    def all_except_delete(self) -> List[str]:
        return [self.view, self.add, self.change]

    @property
    def all(self) -> List[str]:
        return [self.view, self.add, self.change, self.delete]


# class MyBaseSerializer(DjangoJSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Base):
#             return obj.as_json
#         return super().default(obj)


class Base(Model):
    id: int = AutoField(primary_key=True, editable=False)
    objects = Manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial = self.as_dict

    def is_same_model_as(self, other) -> bool:
        if not isinstance(other, Model):
            return False
        if self._meta.concrete_model != other._meta.concrete_model:
            return False
        return True

    def fields_equal(self, other) -> bool:
        if not self.is_same_model_as(other):
            return False
        for field in self._meta.get_fields():
            name = field.name
            if name in ("id", "objects") or field.auto_created:
                continue
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    @property
    def diff(self) -> dict:
        d1 = self._initial
        d2 = self.as_dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if str(v) != str(d2[k])]
        return dict(diffs)

    @property
    def has_changed(self) -> bool:
        return bool(self.diff)

    @property
    def changed_fields(self) -> KeysView:
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    @property
    def as_dict(self) -> dict:
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    @property
    def as_json(self) -> str:
        as_dict = {col: val for col, val in self.as_dict.items() if val is not None}
        return json.dumps(as_dict, cls=DjangoJSONEncoder)

    def str(self):
        return self.as_json

    @property
    def _type(self):
        return self._class.name_

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        if self.has_changed:
            log.info(f"{self._type} {wrap(self.id)} changed: {self.diff}")
        super().save(*args, **kwargs)
        self._initial = self.as_dict

    @classproperty
    def permissions(cls) -> Permissions:
        return Permissions(cls.meta.app_label, cls.name_.lower())
