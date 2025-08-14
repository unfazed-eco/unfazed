import typing as t

from .schema import AdminField


class Field:
    def __init__(
        self,
        name: str,
        readonly: bool = False,
        show: bool = True,
        blank: bool = True,
        choices: t.Tuple[t.Tuple[t.Union[str, int]]] | None = None,
        help_text: str = "",
        default: t.Any = None,
    ) -> None:
        self.name = name
        self.readonly = readonly
        self.show = show
        self.blank = blank
        self.choices: t.Union[tuple, list] = choices or []
        self.help_text = help_text
        self.default = default

    def to_json(self) -> AdminField:
        return AdminField.model_validate(
            {
                "name": self.name,
                "readonly": self.readonly,
                "show": self.show,
                "blank": self.blank,
                "choices": list(self.choices),
                "help_text": self.help_text,
                "default": self.default,
                "type": self.__class__.__name__,
            }
        )


class CharField(Field):
    pass


class IntegerField(Field):
    pass


class EditorField(Field):
    pass


class TextField(Field):
    pass


class TimeField(Field):
    pass


class UploadField(Field):
    pass


class BooleanField(Field):
    pass


class ImageField(Field):
    pass


class JsonField(Field):
    pass


class DatetimeField(Field):
    pass
