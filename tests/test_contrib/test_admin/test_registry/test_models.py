import enum
import typing as t

import pytest
from tortoise import fields as f
from tortoise.models import Model

from tests.apps.admin.account.models import Book, Profile, User
from unfazed.conf import UnfazedSettings, settings
from unfazed.contrib.admin.registry import (
    ActionKwargs,
    ActionOutput,
    BaseModelAdmin,
    ModelAdmin,
    ModelInlineAdmin,
    ToolAdmin,
    action,
    admin_collector,
    fields,
    register,
    site,
)
from unfazed.serializer import Serializer


def test_site() -> None:
    settings["UNFAZED_SETTINGS"] = UnfazedSettings(
        VERSION="0.1.0", PROJECT_NAME="Unfazed Admin"
    )

    ret = site.to_serialize()
    assert ret.title == "Unfazed Admin"

    site.extra = {"foo": "bar"}
    ret = site.to_serialize()
    assert ret.extra == {"foo": "bar"}

    route = site.to_route()  # type: ignore
    assert route is None


class Brand(enum.StrEnum):
    BMW = "BMW"
    BENZ = "BENZ"


class Color(enum.IntEnum):
    RED = 1
    GREEN = 2


class Car(Model):
    id = f.BigIntField(primary_key=True)
    bits = f.BinaryField()
    limited = f.BooleanField()
    brand = f.CharEnumField(enum_type=Brand, default=Brand.BENZ)
    alias = f.CharField(max_length=100)
    year = f.DateField()
    production_datetime = f.DatetimeField(auto_now_add=True)
    release_datetime = f.DatetimeField()
    price = f.DecimalField(max_digits=10, decimal_places=2)
    length = f.FloatField()
    color = f.IntEnumField(enum_type=Color)
    height = f.IntField()
    extra_info: t.Dict = f.JSONField(default={})
    version = f.SmallIntField()
    description = f.TextField()
    usage = f.TimeDeltaField()
    late_used_time = f.TimeField()
    uuid = f.UUIDField()
    override = f.CharField(max_length=100)
    pic = f.CharField(max_length=255)
    created_at = f.BigIntField()

    class Meta:
        table = "car"


def test_base_model_admin() -> None:
    # test get_fields

    class CarSerializer(Serializer):
        class Meta:
            model = Car

        extra: int

    class CarAdmin(BaseModelAdmin):
        serializer = CarSerializer

        image_fields: t.List[str] = ["pic"]
        datetime_fields: t.List[str] = ["created_at"]
        time_fields: t.List[str] = ["late_used_time"]
        editor_fields: t.List[str] = ["alias"]
        readonly_fields: t.List[str] = ["year"]
        not_null_fields: t.List[str] = ["price"]
        json_fields: t.List[str] = ["description"]

    instance = CarAdmin()

    fields = instance.get_fields()

    assert "id" in fields
    assert fields["id"].field_type == "IntegerField"

    assert "bits" in fields
    assert fields["bits"].field_type == "CharField"

    assert "limited" in fields
    assert fields["limited"].field_type == "BooleanField"
    assert fields["limited"].show is True

    assert "brand" in fields
    assert fields["brand"].field_type == "CharField"
    assert fields["brand"].choices == [("BMW", "BMW"), ("BENZ", "BENZ")]

    assert "year" in fields
    assert fields["year"].field_type == "DateField"
    assert fields["year"].readonly is True

    assert "production_datetime" in fields
    assert fields["production_datetime"].field_type == "DatetimeField"

    assert "price" in fields
    assert fields["price"].field_type == "FloatField"
    assert fields["price"].blank is False

    assert "length" in fields
    assert fields["length"].field_type == "FloatField"

    assert "color" in fields
    assert fields["color"].field_type == "IntegerField"
    assert fields["color"].choices == [("RED", 1), ("GREEN", 2)]

    assert "height" in fields
    assert fields["height"].field_type == "IntegerField"

    assert "extra_info" in fields
    assert fields["extra_info"].field_type == "CharField"

    assert "uuid" in fields
    assert fields["uuid"].field_type == "CharField"

    assert "pic" in fields
    assert fields["pic"].field_type == "ImageField"

    assert "created_at" in fields
    assert fields["created_at"].field_type == "DatetimeField"

    assert "alias" in fields
    assert fields["alias"].field_type == "EditorField"

    assert "extra" in fields
    assert fields["extra"].field_type == "IntegerField"


def test_failed_base_model_admin() -> None:
    class CarSerializer(Serializer):
        class Meta:
            model = Car

    class CarAdmin1(BaseModelAdmin):
        pass

    # dont have serializer
    with pytest.raises(ValueError):
        instance = CarAdmin1()
        instance.get_fields()

    class CarAdmin2(BaseModelAdmin):
        serializer = CarSerializer
        list_display = ["not_exist"]

    # dont have field in list_display
    with pytest.raises(ValueError):
        instance2 = CarAdmin2()
        instance2.get_fields()

    class CarAdmin3(BaseModelAdmin):
        serializer = CarSerializer
        datetime_fields = ["not_exist"]

    with pytest.raises(ValueError):
        instance3 = CarAdmin3()
        instance3.get_fields()

    class CarAdmin4(BaseModelAdmin):
        serializer = CarSerializer
        editor_fields = ["not_exist"]

    with pytest.raises(ValueError):
        instance4 = CarAdmin4()
        instance4.get_fields()

    class CarAdmin5(BaseModelAdmin):
        serializer = CarSerializer
        readonly_fields = ["not_exist"]

    with pytest.raises(ValueError):
        instance5 = CarAdmin5()
        instance5.get_fields()

    class CarAdmin6(BaseModelAdmin):
        serializer = CarSerializer
        not_null_fields = ["not_exist"]

    with pytest.raises(ValueError):
        instance6 = CarAdmin6()
        instance6.get_fields()

    class CarAdmin7(BaseModelAdmin):
        serializer = CarSerializer
        json_fields = ["not_exist"]

    with pytest.raises(ValueError):
        instance7 = CarAdmin7()
        instance7.get_fields()

    # image_fields
    class CarAdmin8(BaseModelAdmin):
        serializer = CarSerializer
        image_fields = ["not_exist"]

    with pytest.raises(ValueError):
        instance8 = CarAdmin8()
        instance8.get_fields()

    # wrong datetime_fields
    class CarAdmin9(BaseModelAdmin):
        serializer = CarSerializer
        datetime_fields = ["alias"]

    with pytest.raises(ValueError):
        instance9 = CarAdmin9()
        instance9.get_fields()


def test_model_admin() -> None:
    # test to_serialize
    class CarSerializer(Serializer):
        class Meta:
            model = Car

    class CarAdmin(ModelAdmin):
        serializer = CarSerializer

        editable = False
        help_text = "help_text"
        can_show_all = False
        can_search = False
        search_fields = ["alias"]
        list_per_page = 10
        detail_display = ["alias", "brand"]
        can_add = False
        list_search = ["alias"]
        can_delete = False
        can_edit = False
        list_filter = ["brand"]
        list_sort = ["id"]
        list_order = ["price", "length"]

    instance: ModelAdmin = CarAdmin()

    attrs = instance.get_attrs(list(instance.get_fields().keys()))

    assert attrs.can_add is False
    assert attrs.can_delete is False
    assert attrs.can_edit is False
    assert attrs.can_show_all is False
    assert attrs.can_search is False

    assert attrs.search_fields == ["alias"]
    assert attrs.list_per_page == 10
    assert attrs.detail_display == ["alias", "brand"]

    assert attrs.list_search == ["alias"]
    assert attrs.list_filter == ["brand"]
    assert attrs.list_sort == ["id"]
    assert attrs.list_order == ["price", "length"]

    assert attrs.help_text == "help_text"

    class CarAdmin2(ModelAdmin):
        serializer = CarSerializer

        detail_display = ["not_exist"]

    with pytest.raises(ValueError):
        instance2 = CarAdmin2()
        instance2.get_attrs(list(instance.get_fields().keys()))

    # test to_serialize
    ret = instance.to_serialize()
    assert bool(ret.fields) is True
    assert bool(ret.attrs) is True


@pytest.fixture(autouse=True)
def setup_inline() -> None:
    admin_collector.clear()

    class CarSerializer(Serializer):
        class Meta:
            model = Car

    @register(CarSerializer)
    class CarAdmin(ModelAdmin):
        pass

    class BookSerializer(Serializer):
        class Meta:
            model = Book

    @register(BookSerializer)
    class BookAdmin(ModelAdmin):
        pass

    class UserSerializer(Serializer):
        class Meta:
            model = User

    @register(UserSerializer)
    class UserAdmin1(ModelAdmin):
        inlines = ["BookAdmin"]

    @register(UserSerializer)
    class UserAdmin2(ModelAdmin):
        inlines = ["CarAdmin"]

    @register(UserSerializer)
    class UserAdmin3(ModelAdmin):
        inlines = []

    @register(UserSerializer)
    class InlineUserAdmin4(ModelAdmin):
        pass

    @register(BookSerializer)
    class BookAdmin2(ModelAdmin):
        inlines = ["InlineUserAdmin4"]

    class ProfileSerializer(Serializer):
        class Meta:
            model = Profile

    @register(ProfileSerializer)
    class ProfileAdmin(ModelAdmin):
        inlines = ["InlineUserAdmin4"]


def test_model_admin_inlines() -> None:
    # normal
    instance1: ModelAdmin = admin_collector["UserAdmin1"]
    ret = instance1.to_inlines()

    assert "BookAdmin" in ret

    # no relation
    with pytest.raises(ValueError):
        instance2: ModelAdmin = admin_collector["UserAdmin2"]
        instance2.to_inlines()

    # no inlines
    instance3: ModelAdmin = admin_collector["UserAdmin3"]
    ret3 = instance3.to_inlines()
    assert ret3 == {}

    # bk_fk
    with pytest.raises(ValueError):
        instance4: ModelAdmin = admin_collector["BookAdmin2"]
        instance4.to_inlines()

    # bk_o2o
    with pytest.raises(ValueError):
        instance5: ModelAdmin = admin_collector["ProfileAdmin"]
        instance5.to_inlines()


def test_inline_admin() -> None:
    class BookSerializer(Serializer):
        class Meta:
            model = Book

    class BookAdmin(ModelInlineAdmin):
        serializer = BookSerializer

        help_text = "help_text"
        can_search = False
        search_fields = ["title"]
        can_add = False
        can_delete = False
        can_edit = False
        can_show_all = False

        list_per_page = 10
        list_search = ["title"]
        list_filter = ["author"]
        list_sort = ["id"]
        list_order = ["title", "author"]

        max_num = 10
        min_num = 1

        can_copy = False

    instance = BookAdmin()

    attrs = instance.get_attrs(list(instance.get_fields().keys()))

    assert attrs.can_add is False
    assert attrs.can_delete is False
    assert attrs.can_edit is False
    assert attrs.can_show_all is False
    assert attrs.can_search is False
    assert attrs.max_num == 10
    assert attrs.min_num == 1

    assert attrs.search_fields == ["title"]
    assert attrs.list_per_page == 10
    assert attrs.list_search == ["title"]
    assert attrs.list_filter == ["author"]
    assert attrs.list_sort == ["id"]
    assert attrs.list_order == ["title", "author"]
    assert attrs.help_text == "help_text"

    class BookAdmin1(ModelInlineAdmin):
        serializer = BookSerializer

        list_filter = ["not_exist"]

    with pytest.raises(ValueError):
        instance2 = BookAdmin1()
        instance2.get_attrs(list(instance.get_fields().keys()))

    ret = instance.to_serialize()
    assert bool(ret.fields) is True
    assert bool(ret.attrs) is True


def test_tool_admin() -> None:
    class ExportTool(ToolAdmin):
        fields_set = [
            fields.CharField("name"),
            fields.IntegerField("age"),
            fields.TextField("description"),
            fields.TimeField("late_used_time"),
            fields.UploadField("upload"),
            fields.EditorField("editor"),
            fields.BooleanField("is_active"),
            fields.ImageField("image"),
            fields.JsonField("extra_info"),
            fields.DatetimeField("created_at"),
        ]

        @action(name="export", label="Export", output=ActionOutput.Download)
        async def export(self, ctx: ActionKwargs) -> str:
            return "export"

    instance = ExportTool()

    ret = instance.to_serialize()

    assert bool(ret.fields) is True
    assert bool(ret.attrs) is True
