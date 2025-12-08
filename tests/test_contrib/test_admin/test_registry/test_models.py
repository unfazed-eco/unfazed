import typing as t

import pytest

from tests.apps.admin.registry.models import (
    Car,
    T1Book,
    T2Book,
    T2Role,
    T2User,
    T2UserRole,
)
from unfazed.conf import UnfazedSettings, settings
from unfazed.contrib.admin.registry import (
    ActionKwargs,
    ActionOutput,
    AdminInlineSerializeModel,
    AdminRelation,
    AdminThrough,
    BaseModelAdmin,
    CustomAdmin,
    ModelAdmin,
    ModelInlineAdmin,
    action,
    admin_collector,
    fields,
    register,
    site,
)
from unfazed.contrib.admin.settings import AuthPlugin
from unfazed.serializer import Serializer


def test_site() -> None:
    settings["UNFAZED_SETTINGS"] = UnfazedSettings(
        VERSION="0.1.0", PROJECT_NAME="Unfazed Admin"
    )

    ret = site.to_serialize()
    assert ret.title == "Unfazed Admin"
    assert ret.navTheme == "light"
    assert ret.colorPrimary == "#1890ff"
    assert ret.layout == "mix"
    assert ret.contentWidth == "Fluid"
    assert ret.fixedHeader is False
    assert ret.fixSiderbar is True
    assert ret.colorWeak is False
    assert ret.pwa is False
    assert (
        ret.logo
        == "https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg"
    )

    assert ret.pageSize == 20
    assert ret.timeZone == "UTC"
    assert ret.apiPrefix == "/api/contrib/admin"
    assert ret.debug is True
    assert ret.version == "0.1.0"
    assert ret.authPlugins == [
        AuthPlugin(
            ICON_URL="https://developers.google.com/identity/images/g-logo.png",
            PLATFORM="google",
        )
    ]
    assert ret.extra == {}

    assert ret.iconfontUrl == ""
    assert ret.showWatermark is True

    route = site.to_route()  # type: ignore
    assert route is None


def test_base_admin_label() -> None:
    """Test BaseAdmin.label property when _label is set."""

    class TestAdmin(CustomAdmin):
        _label = "Custom Label"

    admin = TestAdmin()
    assert admin.label == "Custom Label"


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

        @action(name="action1", label="Action 1")
        async def action1(self, ctx: ActionKwargs) -> None:
            pass

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
    assert fields["color"].choices == [(1, "RED"), (2, "GREEN")]

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

    # test permission str generation
    assert instance.view_permission == "models.test_models_car.can_view"
    assert instance.change_permission == "models.test_models_car.can_change"
    assert instance.delete_permission == "models.test_models_car.can_delete"
    assert instance.create_permission == "models.test_models_car.can_create"
    assert (
        instance.action_permission("action1")
        == "models.test_models_car.can_exec_action1"
    )

    assert len(instance.get_all_permissions()) == 5


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
    # test get_attrs with all AdminAttrs properties
    class CarSerializer(Serializer):
        class Meta:
            model = Car

    class CarAdmin(ModelAdmin):
        serializer = CarSerializer

        # BaseAdmin properties
        help_text = "Custom help text for Car admin"

        # BaseModelAdmin properties - boolean flags
        can_add = False
        can_delete = False
        can_edit = False
        can_show_all = False

        # BaseModelAdmin properties - list page configuration
        list_per_page = 15
        list_search = ["alias", "brand"]
        list_filter = ["brand", "color"]
        list_sort = ["id", "price"]
        list_order = ["price", "length", "height"]
        list_editable = ["alias", "price"]

        # ModelAdmin properties - detail page configuration
        detail_display = ["alias", "brand", "price", "year"]
        detail_order = ["id", "alias", "brand"]
        detail_editable = ["alias", "price", "length"]

    instance: ModelAdmin = CarAdmin()
    field_list = list(instance.get_fields().keys())
    attrs = instance.get_attrs(field_list)

    # Test BaseAdmin properties
    assert attrs.help_text == "Custom help text for Car admin"

    # Test boolean flags
    assert attrs.can_add is False
    assert attrs.can_delete is False
    assert attrs.can_edit is False

    # Test list page configuration
    assert attrs.list_per_page == 15
    assert attrs.list_search == ["alias", "brand"]
    assert attrs.list_filter == ["brand", "color"]
    assert attrs.list_sort == ["id", "price"]
    assert attrs.list_order == ["price", "length", "height"]
    assert attrs.list_editable == ["alias", "price"]

    # Test detail page configuration
    assert attrs.detail_display == ["alias", "brand", "price", "year"]
    assert attrs.detail_order == ["id", "alias", "brand"]
    assert attrs.detail_editable == ["alias", "price", "length"]

    # Test default values when not specified
    class CarAdminDefault(ModelAdmin):
        serializer = CarSerializer

    instance_default: ModelAdmin = CarAdminDefault()
    attrs_default = instance_default.get_attrs(
        list(instance_default.get_fields().keys())
    )

    # Test default boolean values
    assert attrs_default.can_add is True
    assert attrs_default.can_delete is True
    assert attrs_default.can_edit is True

    # Test default list configuration
    assert attrs_default.list_per_page == 20
    assert attrs_default.list_search == []
    assert attrs_default.list_filter == []
    assert attrs_default.list_sort == []
    assert attrs_default.list_order == []
    assert attrs_default.list_editable == []

    # Test default detail configuration
    assert attrs_default.detail_order == []
    assert attrs_default.detail_editable == []
    # detail_display defaults to all model fields when empty
    assert len(attrs_default.detail_display) > 0
    # Verify it contains actual model fields
    assert (
        "id" in attrs_default.detail_display or "alias" in attrs_default.detail_display
    )

    # Test detail_display with empty list explicitly
    class CarAdminEmptyDetailDisplay(ModelAdmin):
        serializer = CarSerializer
        detail_display = []

    instance_empty_detail: ModelAdmin = CarAdminEmptyDetailDisplay()
    attrs_empty_detail = instance_empty_detail.get_attrs(
        list(instance_empty_detail.get_fields().keys())
    )
    # When detail_display is empty, it should use all model fields
    assert len(attrs_empty_detail.detail_display) > 0

    # Test default help_text
    assert attrs_default.help_text == ""

    # Test validation - invalid field names
    class CarAdminInvalid(ModelAdmin):
        serializer = CarSerializer
        detail_display = ["not_exist_field"]

    with pytest.raises(ValueError, match="field not_exist_field not found"):
        instance_invalid = CarAdminInvalid()
        instance_invalid.get_attrs(list(instance_invalid.get_fields().keys()))

    # Test validation - invalid field in list_filter
    class CarAdminInvalidFilter(ModelAdmin):
        serializer = CarSerializer
        list_filter = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_filter = CarAdminInvalidFilter()
        instance_invalid_filter.get_attrs(
            list(instance_invalid_filter.get_fields().keys())
        )

    # Test validation - invalid field in list_editable
    class CarAdminInvalidEditable(ModelAdmin):
        serializer = CarSerializer
        list_editable = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_editable = CarAdminInvalidEditable()
        instance_invalid_editable.get_attrs(
            list(instance_invalid_editable.get_fields().keys())
        )

    # Test validation - invalid field in detail_editable
    class CarAdminInvalidDetailEditable(ModelAdmin):
        serializer = CarSerializer
        detail_editable = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_detail_editable = CarAdminInvalidDetailEditable()
        instance_invalid_detail_editable.get_attrs(
            list(instance_invalid_detail_editable.get_fields().keys())
        )

    # Test validation - invalid field in list_sort
    class CarAdminInvalidListSort(ModelAdmin):
        serializer = CarSerializer
        list_sort = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_list_sort = CarAdminInvalidListSort()
        instance_invalid_list_sort.get_attrs(
            list(instance_invalid_list_sort.get_fields().keys())
        )

    # Test validation - invalid field in list_order
    class CarAdminInvalidListOrder(ModelAdmin):
        serializer = CarSerializer
        list_order = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_list_order = CarAdminInvalidListOrder()
        instance_invalid_list_order.get_attrs(
            list(instance_invalid_list_order.get_fields().keys())
        )

    # Test validation - invalid field in list_search
    class CarAdminInvalidListSearch(ModelAdmin):
        serializer = CarSerializer
        list_search = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_list_search = CarAdminInvalidListSearch()
        instance_invalid_list_search.get_attrs(
            list(instance_invalid_list_search.get_fields().keys())
        )

    # Test validation - invalid field in detail_order
    class CarAdminInvalidDetailOrder(ModelAdmin):
        serializer = CarSerializer
        detail_order = ["invalid_field"]

    with pytest.raises(ValueError, match="field invalid_field not found"):
        instance_invalid_detail_order = CarAdminInvalidDetailOrder()
        instance_invalid_detail_order.get_attrs(
            list(instance_invalid_detail_order.get_fields().keys())
        )

    # Test to_serialize method
    ret = instance.to_serialize()
    assert bool(ret.fields) is True
    assert bool(ret.attrs) is True
    assert ret.attrs.help_text == "Custom help text for Car admin"
    assert ret.attrs.can_add is False
    assert ret.attrs.list_per_page == 15
    assert ret.attrs.detail_display == ["alias", "brand", "price", "year"]


def test_model_admin_inlines_with_relation_fields(setup_inline: None) -> None:
    assert "T1UserAdmin" in admin_collector
    user_admin: ModelAdmin = admin_collector["T1UserAdmin"]

    ret = user_admin.to_inlines()

    assert "T1BookAdmin" in ret
    assert "T1ProfileAdmin" in ret
    assert "T1RoleAdmin" in ret

    # bk_fk
    t1_book_admin: AdminInlineSerializeModel = ret["T1BookAdmin"]
    assert t1_book_admin.relation is not None

    assert t1_book_admin.relation.target == "T1BookAdmin"
    assert t1_book_admin.relation.source_field == "id"
    assert t1_book_admin.relation.target_field == "owner_id"
    assert t1_book_admin.relation.relation == "bk_fk"

    # o2o
    t1_profile_admin: AdminInlineSerializeModel = ret["T1ProfileAdmin"]
    assert t1_profile_admin.relation is not None

    assert t1_profile_admin.relation.target == "T1ProfileAdmin"
    assert t1_profile_admin.relation.source_field == "id"
    assert t1_profile_admin.relation.target_field == "user_id"
    assert t1_profile_admin.relation.relation == "bk_o2o"

    # m2m
    t1_role_admin: AdminInlineSerializeModel = ret["T1RoleAdmin"]
    assert t1_role_admin.relation is not None
    assert t1_role_admin.relation.target == "T1RoleAdmin"
    assert t1_role_admin.relation.relation == "m2m"
    assert t1_role_admin.relation.through is not None
    assert t1_role_admin.relation.through.through == "T1UserRoleAdmin"
    assert t1_role_admin.relation.through.source_field == "id"
    assert t1_role_admin.relation.through.source_to_through_field == "user_id"
    assert t1_role_admin.relation.through.target_field == "id"
    assert t1_role_admin.relation.through.target_to_through_field == "role_id"


def test_model_admin_inlines_without_relation_fields(setup_inline: None) -> None:
    assert "T2UserAdmin" in admin_collector
    user_admin: ModelAdmin = admin_collector["T2UserAdmin"]

    ret = user_admin.to_inlines()

    assert "T2BookAdmin" in ret
    assert "T2ProfileAdmin" in ret
    assert "T2RoleAdmin" in ret

    # bk_fk
    t2_book_admin: AdminInlineSerializeModel = ret["T2BookAdmin"]
    assert t2_book_admin.relation is not None

    assert t2_book_admin.relation.target == "T2BookAdmin"
    assert t2_book_admin.relation.source_field == "id"
    assert t2_book_admin.relation.target_field == "owner_id"
    assert t2_book_admin.relation.relation == "bk_fk"

    # o2o
    t2_profile_admin: AdminInlineSerializeModel = ret["T2ProfileAdmin"]
    assert t2_profile_admin.relation is not None

    assert t2_profile_admin.relation.target == "T2ProfileAdmin"
    assert t2_profile_admin.relation.source_field == "id"
    assert t2_profile_admin.relation.target_field == "user_id"
    assert t2_profile_admin.relation.relation == "bk_o2o"

    # m2m

    t2_role_admin: AdminInlineSerializeModel = ret["T2RoleAdmin"]
    assert t2_role_admin.relation is not None
    assert t2_role_admin.relation.target == "T2RoleAdmin"
    assert t2_role_admin.relation.relation == "m2m"
    assert t2_role_admin.relation.through is not None
    assert t2_role_admin.relation.through.through == "T2UserRoleAdmin"
    assert t2_role_admin.relation.through.source_field == "id"
    assert t2_role_admin.relation.through.source_to_through_field == "user_id"
    assert t2_role_admin.relation.through.target_field == "id"
    assert t2_role_admin.relation.through.target_to_through_field == "role_id"


def test_model_admin_failed() -> None:
    class T3UserSerializer(Serializer):
        class Meta:
            model = T2User

    class T3BookSerializer(Serializer):
        class Meta:
            model = T2Book

    class T3RoleSerializer(Serializer):
        class Meta:
            model = T2Role

    class T3UserRoleSerializer(Serializer):
        class Meta:
            model = T2UserRole

    class T3CarSerializer(Serializer):
        class Meta:
            model = Car

    @register(T3UserSerializer)
    class T3UserAdmin(ModelAdmin):
        inlines = [AdminRelation(target="T3BookAdmin")]

    @register(T3BookSerializer)
    class T3BookAdmin(ModelAdmin):
        pass

    # admin in inlines must be ModelInlineAdmin
    with pytest.raises(ValueError):
        instance = admin_collector["T3UserAdmin"]
        instance.to_inlines()

    @register(T3UserSerializer)
    class T4UserAdmin(ModelAdmin):
        inlines = [AdminRelation(target="T4CarAdmin")]

    @register(T3CarSerializer)
    class T4CarAdmin(ModelInlineAdmin):
        pass

    instance4 = admin_collector["T4UserAdmin"]
    # it must have relation between inlines and admin
    with pytest.raises(ValueError):
        instance4.to_inlines()

    instance4.inlines = [
        AdminRelation(
            target="T4CarAdmin",
            relation="bk_fk",
            source_field="not_exist",
            target_field="owner_id",
        )
    ]

    with pytest.raises(ValueError):
        instance4.to_inlines()

    instance4.inlines = [
        AdminRelation(
            target="T4CarAdmin",
            relation="bk_fk",
            source_field="id",
            target_field="not_exist",
        )
    ]

    with pytest.raises(ValueError):
        instance4.to_inlines()

    @register(T3UserSerializer)
    class T5UserAdmin(ModelAdmin):
        inlines = [
            AdminRelation(
                target="T5RoleAdmin",
                relation="m2m",
                through=AdminThrough(
                    through="T5UserRoleAdmin",
                    source_field="not_exist",
                    source_to_through_field="user_id",
                    target_field="id",
                    target_to_through_field="role_id",
                ),
            )
        ]

    @register(T3RoleSerializer)
    class T5RoleAdmin(ModelInlineAdmin):
        pass

    @register(T3UserRoleSerializer)
    class T5UserRoleAdmin(ModelInlineAdmin):
        pass

    # it must have relation between inlines and admin
    instance5 = admin_collector["T5UserAdmin"]
    with pytest.raises(ValueError):
        instance5.to_inlines()

    instance5.inlines = [
        AdminRelation(
            target="T5RoleAdmin",
            relation="m2m",
            through=AdminThrough(
                through="T5UserRoleAdmin",
                source_field="id",
                source_to_through_field="not_exist",
                target_field="id",
                target_to_through_field="role_id",
            ),
        )
    ]

    with pytest.raises(ValueError):
        instance5.to_inlines()

    instance5.inlines = [
        AdminRelation(
            target="T5RoleAdmin",
            relation="m2m",
            through=AdminThrough(
                through="T5UserRoleAdmin",
                source_field="id",
                source_to_through_field="user_id",
                target_field="not_exist",
                target_to_through_field="role_id",
            ),
        )
    ]

    with pytest.raises(ValueError):
        instance5.to_inlines()

    instance5.inlines = [
        AdminRelation(
            target="T5RoleAdmin",
            relation="m2m",
            through=AdminThrough(
                through="T5UserRoleAdmin",
                source_field="id",
                source_to_through_field="user_id",
                target_field="id",
                target_to_through_field="not_exist",
            ),
        )
    ]

    with pytest.raises(ValueError):
        instance5.to_inlines()


def test_inline_admin() -> None:
    # test get_attrs with all AdminInlineAttrs properties
    class BookSerializer(Serializer):
        class Meta:
            model = T1Book

    class BookAdmin(ModelInlineAdmin):
        serializer = BookSerializer

        # BaseAdmin properties
        help_text = "Custom help text for Book inline admin"

        # BaseModelAdmin properties - boolean flags
        can_add = False
        can_delete = False
        can_edit = False

        # BaseModelAdmin properties - list page configuration
        list_per_page = 15
        list_search = ["title"]
        list_filter = ["owner_id"]
        list_sort = ["id", "title"]
        list_order = ["title", "owner_id"]
        list_editable = ["title"]

        # ModelInlineAdmin properties
        max_num = 10
        min_num = 1

    instance: ModelInlineAdmin = BookAdmin()
    field_list = list(instance.get_fields().keys())
    attrs = instance.get_attrs(field_list)

    # Test BaseAdmin properties
    assert attrs.help_text == "Custom help text for Book inline admin"

    # Test boolean flags
    assert attrs.can_add is False
    assert attrs.can_delete is False
    assert attrs.can_edit is False

    # Test list page configuration
    assert attrs.list_per_page == 15
    assert attrs.list_search == ["title"]
    assert attrs.list_filter == ["owner_id"]
    assert attrs.list_sort == ["id", "title"]
    assert attrs.list_order == ["title", "owner_id"]
    assert attrs.list_editable == ["title"]

    # Test ModelInlineAdmin specific properties
    assert attrs.max_num == 10
    assert attrs.min_num == 1

    # Test default values when not specified
    class BookAdminDefault(ModelInlineAdmin):
        serializer = BookSerializer

    instance_default: ModelInlineAdmin = BookAdminDefault()
    attrs_default = instance_default.get_attrs(
        list(instance_default.get_fields().keys())
    )

    # Test default boolean values
    assert attrs_default.can_add is True
    assert attrs_default.can_delete is True
    assert attrs_default.can_edit is True

    # Test default list configuration
    assert attrs_default.list_per_page == 20
    assert attrs_default.list_search == []
    assert attrs_default.list_filter == []
    assert attrs_default.list_sort == []
    assert attrs_default.list_order == []
    assert attrs_default.list_editable == []

    # Test default ModelInlineAdmin properties
    assert attrs_default.max_num == 0
    assert attrs_default.min_num == 0

    # Test default help_text
    assert attrs_default.help_text == ""

    # Test validation - invalid field names
    class BookAdminInvalid(ModelInlineAdmin):
        serializer = BookSerializer
        list_filter = ["not_exist_field"]

    with pytest.raises(ValueError, match="field not_exist_field not found"):
        instance_invalid = BookAdminInvalid()
        instance_invalid.get_attrs(list(instance_invalid.get_fields().keys()))

    # Test validation - invalid field in list_search
    class BookAdminInvalidListSearch(ModelInlineAdmin):
        serializer = BookSerializer
        list_search = ["invalid_field"]

    with pytest.raises(ValueError):
        instance_invalid_list_search = BookAdminInvalidListSearch()
        instance_invalid_list_search.get_attrs(
            list(instance_invalid_list_search.get_fields().keys())
        )

    # Test validation - invalid field in list_sort
    class BookAdminInvalidListSort(ModelInlineAdmin):
        serializer = BookSerializer
        list_sort = ["invalid_field"]

    with pytest.raises(ValueError):
        instance_invalid_list_sort = BookAdminInvalidListSort()
        instance_invalid_list_sort.get_attrs(
            list(instance_invalid_list_sort.get_fields().keys())
        )

    # Test validation - invalid field in list_order
    class BookAdminInvalidListOrder(ModelInlineAdmin):
        serializer = BookSerializer
        list_order = ["invalid_field"]

    with pytest.raises(ValueError):
        instance_invalid_list_order = BookAdminInvalidListOrder()
        instance_invalid_list_order.get_attrs(
            list(instance_invalid_list_order.get_fields().keys())
        )

    # Test validation - invalid field in list_editable
    class BookAdminInvalidListEditable(ModelInlineAdmin):
        serializer = BookSerializer
        list_editable = ["invalid_field"]

    with pytest.raises(ValueError):
        instance_invalid_list_editable = BookAdminInvalidListEditable()
        instance_invalid_list_editable.get_attrs(
            list(instance_invalid_list_editable.get_fields().keys())
        )

    # Test validation - invalid field in list_display
    class BookAdminInvalidListDisplay(ModelInlineAdmin):
        serializer = BookSerializer
        list_display = ["invalid_field"]

    with pytest.raises(ValueError):
        instance_invalid_list_display = BookAdminInvalidListDisplay()
        instance_invalid_list_display.get_attrs(
            list(instance_invalid_list_display.get_fields().keys())
        )

    # Test to_serialize method
    ret = instance.to_serialize()
    assert bool(ret.fields) is True
    assert bool(ret.attrs) is True
    assert ret.attrs.help_text == "Custom help text for Book inline admin"
    assert ret.attrs.can_add is False
    assert ret.attrs.list_per_page == 15
    assert ret.attrs.max_num == 10
    assert ret.attrs.min_num == 1
    assert ret.attrs.list_editable == ["title"]

    # Test to_route method - should return None for inline admin
    route_ret = instance.to_route()  # type: ignore
    assert route_ret is None


def test_tool_admin() -> None:
    class ExportTool(CustomAdmin):
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

    # test permission str generation
    assert instance.view_permission == "custom.exporttool.can_view"
    assert instance.action_permission("export") == "custom.exporttool.can_exec_export"

    assert len(instance.get_all_permissions()) == 2
