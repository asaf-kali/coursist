import json
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import KeysView, List, Dict, Tuple

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import model_to_dict
from django.utils.decorators import classproperty

from academic_helper.utils.logger import log, wrap

ReadableEnum = namedtuple("ReadableEnum", ["value", "name"])


class ChoicesEnum(Enum):
    @classmethod
    def as_dict(cls) -> Dict[int, str]:
        return {e.name: e.value for e in cls.readable_list()}

    @classmethod
    def list(cls) -> List[Tuple[int, str]]:
        """
        :return: a list of tuples, representing all enum options.
        Each enum tuple is (value, name), where value is the enum value and name is the parsed
        readable ("Title Styled") name of the enum.
        Used for django's IntegerField options.
        """
        return list(map(enum_to_tuple, cls))

    @classmethod
    def readable_list(cls) -> List[ReadableEnum]:
        """
        :return: a list of ReadableEnum instances representing all enum options.
        Used for convenient template rendering (using field names and not tuple indexes).
        """
        return [ReadableEnum(*t) for t in cls.list()]

    @property
    def readable_name(self):
        return " ".join(c.capitalize() or "" for c in self.name.split("_"))


def enum_to_tuple(enum: ChoicesEnum) -> Tuple:
    return enum.value, enum.readable_name


@dataclass
class Permissions:
    _app_name: str
    _obj_name: str

    def _get_permission(self, name: str) -> str:
        return f"{self._app_name}.{name}{self._obj_name}"

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


class Base(models.Model):
    id: int = models.AutoField(primary_key=True, editable=False)
    objects = models.Manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial = self.as_dict

    def is_same_model_as(self, other) -> bool:
        if not isinstance(other, models.Model):
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
        # TODO: Check this out!
        # return model_to_dict(self, fields=[field.name for field in self._meta.fields])
        return dict()

    @property
    def as_json(self) -> str:
        as_dict = {col: val for col, val in self.as_dict.items() if val is not None}
        return json.dumps(as_dict, cls=DjangoJSONEncoder)

    def str(self):
        return self.as_json

    @property
    def verbose_type(self):
        return self._meta.verbose_name.title()

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        if self.has_changed:
            # TODO: solve hebrew encoding issue
            log.info(f"{self.verbose_type} {wrap(self.id)} changed: {self.diff}".encode("utf-8"))
        super().save(*args, **kwargs)
        self._initial = self.as_dict

    @classproperty
    def permissions(cls) -> Permissions:
        return Permissions(cls._meta.app_label, cls._meta.model_name)
