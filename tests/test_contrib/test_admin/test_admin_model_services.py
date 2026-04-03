import datetime
import typing as t
import uuid

import pytest

from tests.apps.admin.registry.models import (
    Brand,
    Car,
    Color,
    T1Book,
    T1Role,
    T1User,
    T1UserRole,
    T2Book,
    T2Role,
    T2User,
    T2UserRole,
)
from unfazed.contrib.admin.registry import (
    ActionKwargs,
    ModelAdmin,
    action,
    admin_collector,
    register,
)
from unfazed.contrib.admin.schema import Action
from unfazed.contrib.admin.services import AdminModelService
from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest
from unfazed.serializer import Serializer


class _SuperUser:
    is_superuser = True


def build_request() -> HttpRequest:
    request = HttpRequest(scope={"type": "http", "method": "GET", "user": _SuperUser()})
    return request


@pytest.fixture
async def setup_without_relation_env() -> t.AsyncGenerator:
    await Car.all().delete()

    for i in range(20):
        car = Car(
            bits=b"bits",
            limited=i % 2 == 0,
            brand=Brand.BENZ,
            alias=f"alias_{i}",
            year=datetime.date(2025, 1, 1),
            production_datetime=datetime.datetime.now(),
            release_datetime=datetime.datetime.now(),
            price=i * 1000,
            length=i * 100,
            color=Color.RED,
            height=i * 100,
            extra_info={"extra_info": f"extra_info_{i}"},
            version=i % 2,
            description=f"description_{i}",
            usage=datetime.timedelta(days=i),
            late_used_time=datetime.time(hour=i),
            uuid=uuid.uuid4(),
            override=f"override_{i}",
            pic=f"pic_{i}",
            created_at=i,
        )
        await car.save()

    yield

    await Car.all().delete()


@pytest.fixture
async def setup_inlines_with_relation_fields() -> t.AsyncGenerator:
    await T1User.all().delete()

    for i in range(20):
        user = T1User(
            name=f"user_{i}",
            email=f"user_{i}@example.com",
            password=f"password_{i}",
        )
        await user.save()

    yield

    await T1User.all().delete()


@pytest.fixture
async def setup_inlines_without_relation_fields() -> t.AsyncGenerator:
    await T2User.all().delete()

    for i in range(20):
        user = T2User(
            name=f"user_{i}",
            email=f"user_{i}@example.com",
            password=f"password_{i}",
        )
        await user.save()

    yield

    await T2User.all().delete()


async def test_admin_services_without_relations(
    setup_without_relation_env: None,
) -> None:
    class CarSerializer(Serializer):
        class Meta:
            model = Car

    @register(CarSerializer)
    class TSCarAdmin(ModelAdmin):
        @action(name="test_action")
        def test_action(self, ctx: ActionKwargs) -> str:
            return "test_action"

    desc_ret = await AdminModelService.model_desc("TSCarAdmin", build_request())

    assert desc_ret.attrs is not None
    assert desc_ret.fields is not None
    assert desc_ret.actions is not None

    data_ret = await AdminModelService.model_data(
        "TSCarAdmin", [], 1, 10, build_request()
    )
    assert data_ret is not None
    assert data_ret.count == 20
    assert data_ret.data is not None
    assert len(data_ret.data) == 10

    instance = await Car.get(created_at=1)

    inlines_ret = await AdminModelService.model_inlines(
        "TSCarAdmin", {"id": instance.id}, build_request()
    )
    assert not inlines_ret

    # create

    new_car_dict = {
        "id": -1,
        "bits": b"bits",
        "limited": True,
        "brand": Brand.BENZ,
        "alias": "alias_1",
        "year": datetime.date(2025, 1, 1),
        "production_datetime": datetime.datetime.now(),
        "release_datetime": datetime.datetime.now(),
        "price": 1000,
        "length": 100,
        "color": Color.RED,
        "height": 100,
        "extra_info": {"extra_info": "extra_info_1"},
        "version": 1,
        "description": "description_1",
        "usage": datetime.timedelta(days=1),
        "late_used_time": datetime.time(hour=1),
        "uuid": uuid.uuid4(),
        "override": "override_1",
        "pic": "pic_1",
        "created_at": 10000,
    }
    save_ret = await AdminModelService.model_save(
        "TSCarAdmin", new_car_dict, build_request()
    )

    assert save_ret is not None
    assert save_ret.id is not None
    assert save_ret.id > 0

    assert (await Car.get(id=save_ret.id)) is not None

    # update

    update_car_dict = new_car_dict.copy()
    update_car_dict["id"] = save_ret.id
    update_car_dict["alias"] = "alias_2"

    update_ret = await AdminModelService.model_save(
        "TSCarAdmin", update_car_dict, build_request()
    )

    assert update_ret is not None
    assert update_ret.id is not None
    assert update_ret.id > 0
    assert update_ret.alias == "alias_2"

    assert (await Car.get(id=update_ret.id)) is not None

    # delete

    await AdminModelService.model_delete(
        "TSCarAdmin", {"id": update_ret.id}, build_request()
    )

    assert (await Car.get_or_none(id=update_ret.id)) is None

    # delete non-existed

    with pytest.raises(ValueError):
        await AdminModelService.model_delete("TSCarAdmin", {"id": -1}, build_request())

    # action

    action_ret = await AdminModelService.model_action(
        Action(
            name="TSCarAdmin",
            action="test_action",
            search_condition=[],
        ),
        build_request(),
    )
    assert action_ret is not None
    assert action_ret == "test_action"

    # non-existed action

    with pytest.raises(KeyError):
        await AdminModelService.model_action(
            Action(
                name="TSCarAdmin",
                action="non_existed_action",
                search_condition=[],
            ),
            build_request(),
        )


async def test_admin_services_hooks(
    setup_without_relation_env: None,
) -> None:
    event_log: list[tuple[str, t.Any]] = []

    class HookCarSerializer(Serializer):
        class Meta:
            model = Car

    @register(HookCarSerializer)
    class HookCarAdmin(ModelAdmin):
        async def before_save(
            self, serializer: Serializer, *args: t.Any, **kwargs: t.Any
        ) -> Serializer:
            serializer.alias = f"hooked-{serializer.alias}"
            event_log.append(("before_save", serializer.alias))
            return serializer

        async def after_save(
            self, instance: Car, *args: t.Any, **kwargs: t.Any
        ) -> Car:
            event_log.append(("after_save", instance.alias))
            return instance

        async def before_delete(
            self, instance: Car, *args: t.Any, **kwargs: t.Any
        ) -> Car:
            event_log.append(("before_delete", instance.alias))
            return instance

        async def after_delete(
            self, instance: Car, *args: t.Any, **kwargs: t.Any
        ) -> Car:
            event_log.append(("after_delete", instance.alias))
            return instance

    car_dict = {
        "id": -1,
        "bits": b"bits",
        "limited": True,
        "brand": Brand.BENZ,
        "alias": "hook-target",
        "year": datetime.date(2025, 1, 1),
        "production_datetime": datetime.datetime.now(),
        "release_datetime": datetime.datetime.now(),
        "price": 1000,
        "length": 100,
        "color": Color.RED,
        "height": 100,
        "extra_info": {"extra_info": "extra_info_1"},
        "version": 1,
        "description": "description_1",
        "usage": datetime.timedelta(days=1),
        "late_used_time": datetime.time(hour=1),
        "uuid": uuid.uuid4(),
        "override": "override_1",
        "pic": "pic_1",
        "created_at": 10001,
    }

    save_ret = await AdminModelService.model_save(
        "HookCarAdmin", car_dict, build_request()
    )

    assert save_ret.alias == "hooked-hook-target"
    saved_ins = await Car.get(id=save_ret.id)
    assert saved_ins.alias == "hooked-hook-target"
    assert event_log[:2] == [
        ("before_save", "hooked-hook-target"),
        ("after_save", "hooked-hook-target"),
    ]

    await AdminModelService.model_delete(
        "HookCarAdmin", {"id": save_ret.id}, build_request()
    )

    assert (await Car.get_or_none(id=save_ret.id)) is None
    assert event_log[2:] == [
        ("before_delete", "hooked-hook-target"),
        ("after_delete", "hooked-hook-target"),
    ]


async def test_admin_batch_services_hooks(
    setup_without_relation_env: None,
) -> None:
    event_log: list[tuple[str, t.Any]] = []

    class BatchHookCarSerializer(Serializer):
        class Meta:
            model = Car

    @register(BatchHookCarSerializer)
    class BatchHookCarAdmin(ModelAdmin):
        async def batch_before_save(
            self, serializers: t.List[Serializer], *args: t.Any, **kwargs: t.Any
        ) -> t.List[Serializer]:
            for serializer in serializers:
                serializer.alias = f"batch-{serializer.alias}"
            event_log.append(("batch_before_save", [s.alias for s in serializers]))
            return serializers

        async def batch_after_save(
            self, instances: t.List[Car], *args: t.Any, **kwargs: t.Any
        ) -> t.List[Car]:
            event_log.append(
                ("batch_after_save", [instance.alias for instance in instances])
            )
            return instances

    await AdminModelService.batch_model_save(
        "BatchHookCarAdmin",
        [
            {
                "id": -1,
                "bits": b"bits",
                "limited": True,
                "brand": Brand.BENZ,
                "alias": "one",
                "year": datetime.date(2025, 1, 1),
                "production_datetime": datetime.datetime.now(),
                "release_datetime": datetime.datetime.now(),
                "price": 1000,
                "length": 100,
                "color": Color.RED,
                "height": 100,
                "extra_info": {"extra_info": "extra_info_1"},
                "version": 1,
                "description": "description_1",
                "usage": datetime.timedelta(days=1),
                "late_used_time": datetime.time(hour=1),
                "uuid": uuid.uuid4(),
                "override": "override_1",
                "pic": "pic_1",
                "created_at": 11001,
            },
            {
                "id": -1,
                "bits": b"bits",
                "limited": True,
                "brand": Brand.BENZ,
                "alias": "two",
                "year": datetime.date(2025, 1, 1),
                "production_datetime": datetime.datetime.now(),
                "release_datetime": datetime.datetime.now(),
                "price": 2000,
                "length": 200,
                "color": Color.RED,
                "height": 200,
                "extra_info": {"extra_info": "extra_info_2"},
                "version": 1,
                "description": "description_2",
                "usage": datetime.timedelta(days=2),
                "late_used_time": datetime.time(hour=2),
                "uuid": uuid.uuid4(),
                "override": "override_2",
                "pic": "pic_2",
                "created_at": 11002,
            },
        ],
        build_request(),
    )

    saved_cars = await Car.filter(created_at__in=[11001, 11002]).order_by("created_at")
    assert [car.alias for car in saved_cars] == ["batch-one", "batch-two"]
    assert event_log == [
        ("batch_before_save", ["batch-one", "batch-two"]),
        ("batch_after_save", ["batch-one", "batch-two"]),
    ]


async def test_admin_batch_services_atomic(
    setup_without_relation_env: None,
) -> None:
    class AtomicCarSerializer(Serializer):
        class Meta:
            model = Car

    @register(AtomicCarSerializer)
    class AtomicCarAdmin(ModelAdmin):
        pass

    with pytest.raises(Exception):
        await AdminModelService.batch_model_save(
            "AtomicCarAdmin",
            [
                {
                    "id": -1,
                    "bits": b"bits",
                    "limited": True,
                    "brand": Brand.BENZ,
                    "alias": "atomic-one",
                    "year": datetime.date(2025, 1, 1),
                    "production_datetime": datetime.datetime.now(),
                    "release_datetime": datetime.datetime.now(),
                    "price": 1000,
                    "length": 100,
                    "color": Color.RED,
                    "height": 100,
                    "extra_info": {"extra_info": "extra_info_1"},
                    "version": 1,
                    "description": "description_1",
                    "usage": datetime.timedelta(days=1),
                    "late_used_time": datetime.time(hour=1),
                    "uuid": uuid.uuid4(),
                    "override": "override_1",
                    "pic": "pic_1",
                    "created_at": 12001,
                },
                {
                    "id": 999999,
                    "bits": b"bits",
                    "limited": True,
                    "brand": Brand.BENZ,
                    "alias": "atomic-two",
                    "year": datetime.date(2025, 1, 1),
                    "production_datetime": datetime.datetime.now(),
                    "release_datetime": datetime.datetime.now(),
                    "price": 2000,
                    "length": 200,
                    "color": Color.RED,
                    "height": 200,
                    "extra_info": {"extra_info": "extra_info_2"},
                    "version": 1,
                    "description": "description_2",
                    "usage": datetime.timedelta(days=2),
                    "late_used_time": datetime.time(hour=2),
                    "uuid": uuid.uuid4(),
                    "override": "override_2",
                    "pic": "pic_2",
                    "created_at": 12002,
                },
            ],
            build_request(),
        )

    assert await Car.get_or_none(created_at=12001) is None


async def test_admin_batch_services_update_path(
    setup_without_relation_env: None,
) -> None:
    class UpdateBatchCarSerializer(Serializer):
        class Meta:
            model = Car

    @register(UpdateBatchCarSerializer)
    class UpdateBatchCarAdmin(ModelAdmin):
        pass

    existing = await Car.get(created_at=1)

    await AdminModelService.batch_model_save(
        "UpdateBatchCarAdmin",
        [
            {
                "id": existing.id,
                "bits": existing.bits,
                "limited": existing.limited,
                "brand": existing.brand,
                "alias": "updated-in-batch",
                "year": existing.year,
                "production_datetime": existing.production_datetime,
                "release_datetime": existing.release_datetime,
                "price": existing.price,
                "length": existing.length,
                "color": existing.color,
                "height": existing.height,
                "extra_info": existing.extra_info,
                "version": existing.version,
                "description": existing.description,
                "usage": existing.usage,
                "late_used_time": existing.late_used_time,
                "uuid": existing.uuid,
                "override": existing.override,
                "pic": existing.pic,
                "created_at": existing.created_at,
            }
        ],
        build_request(),
    )

    refreshed = await Car.get(id=existing.id)
    assert refreshed.alias == "updated-in-batch"


async def test_admin_services_inlines_with_relation_fields(
    setup_inline: None,
    setup_inlines_with_relation_fields: t.AsyncGenerator,
) -> None:
    desc_ret = await AdminModelService.model_desc("T1UserAdmin", build_request())

    assert desc_ret.attrs is not None
    assert desc_ret.fields is not None
    assert desc_ret.actions is not None

    data_ret = await AdminModelService.model_data(
        "T1UserAdmin", [], 1, 10, build_request()
    )

    assert data_ret is not None
    assert data_ret.count == 20
    assert data_ret.data is not None
    assert len(data_ret.data) == 10

    user1 = await T1User.create(
        name="user_1", email="user_1@example.com", password="password_1"
    )

    instance = await T1User.get(id=user1.id)

    inlines_ret = await AdminModelService.model_inlines(
        "T1UserAdmin", {"id": instance.id}, build_request()
    )

    assert inlines_ret is not None
    assert inlines_ret["T1BookAdmin"] is not None
    assert inlines_ret["T1ProfileAdmin"] is not None
    assert inlines_ret["T1RoleAdmin"] is not None

    # save
    new_t1_user_dict = {
        "id": -1,
        "name": "user_1",
        "email": "user_1@example.com",
        "password": "password_1",
    }
    user_save_ret = await AdminModelService.model_save(
        "T1UserAdmin", new_t1_user_dict, build_request()
    )

    assert user_save_ret is not None
    assert user_save_ret.id is not None
    assert user_save_ret.id > 0

    assert (await T1User.get(id=user_save_ret.id)) is not None

    # save fk inline model
    new_t1_book_dict = {
        "id": -1,
        "title": "book_1",
        "owner_id": user_save_ret.id,
    }
    book_save_ret = await AdminModelService.model_save(
        "T1BookAdmin", new_t1_book_dict, build_request()
    )

    assert book_save_ret is not None
    assert book_save_ret.id is not None
    assert book_save_ret.id > 0

    assert (await T1Book.get(id=book_save_ret.id)) is not None

    # save o2o inline model
    new_t1_profile_dict = {
        "id": -1,
        "user_id": user_save_ret.id,
    }
    profile_save_ret = await AdminModelService.model_save(
        "T1ProfileAdmin", new_t1_profile_dict, build_request()
    )

    assert profile_save_ret is not None
    assert profile_save_ret.id is not None
    assert profile_save_ret.id > 0

    # save m2m inline model
    role1 = await T1Role.create(name="role_1")

    new_t1_user_role_dict = {
        "id": -1,
        "user_id": user_save_ret.id,
        "role_id": role1.id,
    }
    user_role_save_ret = await AdminModelService.model_save(
        "T1UserRoleAdmin", new_t1_user_role_dict, build_request()
    )

    assert user_role_save_ret is not None
    assert user_role_save_ret.id is not None
    assert user_role_save_ret.id > 0

    assert (await T1UserRole.get(id=user_role_save_ret.id)) is not None


async def test_admin_services_inlines_without_relation_fields(
    setup_inline: None,
    setup_inlines_without_relation_fields: t.AsyncGenerator,
) -> None:
    desc_ret = await AdminModelService.model_desc("T2UserAdmin", build_request())

    assert desc_ret.attrs is not None
    assert desc_ret.fields is not None
    assert desc_ret.actions is not None

    data_ret = await AdminModelService.model_data(
        "T2UserAdmin", [], 1, 10, build_request()
    )

    assert data_ret is not None
    assert data_ret.count == 20
    assert data_ret.data is not None
    assert len(data_ret.data) == 10

    user1 = await T2User.create(
        name="user_1", email="user_1@example.com", password="password_1"
    )

    instance = await T2User.get(id=user1.id)

    inlines_ret = await AdminModelService.model_inlines(
        "T2UserAdmin", {"id": instance.id}, build_request()
    )

    assert inlines_ret is not None
    assert inlines_ret["T2BookAdmin"] is not None
    assert inlines_ret["T2ProfileAdmin"] is not None
    assert inlines_ret["T2RoleAdmin"] is not None

    # save
    new_t2_user_dict = {
        "id": -1,
        "name": "user_1",
        "email": "user_1@example.com",
        "password": "password_1",
    }
    user_save_ret = await AdminModelService.model_save(
        "T2UserAdmin", new_t2_user_dict, build_request()
    )

    assert user_save_ret is not None
    assert user_save_ret.id is not None
    assert user_save_ret.id > 0

    assert (await T2User.get(id=user_save_ret.id)) is not None

    # save fk inline model (without relation field)
    new_t2_book_dict = {
        "id": -1,
        "title": "book_1",
        "owner_id": user_save_ret.id,
    }
    book_save_ret = await AdminModelService.model_save(
        "T2BookAdmin", new_t2_book_dict, build_request()
    )

    assert book_save_ret is not None
    assert book_save_ret.id is not None
    assert book_save_ret.id > 0

    assert (await T2Book.get(id=book_save_ret.id)) is not None

    # save o2o inline model (without relation field)
    new_t2_profile_dict = {
        "id": -1,
        "user_id": user_save_ret.id,
    }
    profile_save_ret = await AdminModelService.model_save(
        "T2ProfileAdmin", new_t2_profile_dict, build_request()
    )

    assert profile_save_ret is not None
    assert profile_save_ret.id is not None
    assert profile_save_ret.id > 0

    # save m2m inline model (without relation field)
    role1 = await T2Role.create(name="role_1")

    new_t2_user_role_dict = {
        "id": -1,
        "user_id": user_save_ret.id,
        "role_id": role1.id,
    }
    user_role_save_ret = await AdminModelService.model_save(
        "T2UserRoleAdmin", new_t2_user_role_dict, build_request()
    )

    assert user_role_save_ret is not None
    assert user_role_save_ret.id is not None
    assert user_role_save_ret.id > 0

    assert (await T2UserRole.get(id=user_role_save_ret.id)) is not None


class _WithoutSuperUser:
    is_superuser = False


class WithoutSuperRequest:
    user = _WithoutSuperUser()


def build_request_without_super() -> HttpRequest:
    request = HttpRequest(
        scope={"type": "http", "method": "GET", "user": _WithoutSuperUser()}
    )
    return request


async def test_permission_denied() -> None:
    admin_collector.clear()

    class CarSerializer(Serializer):
        class Meta:
            model = Car

    @register(CarSerializer)
    class TSCarAdmin(ModelAdmin):
        @action(name="test_action")
        def test_action(self, ctx: ActionKwargs) -> str:
            return "test_action"

    request = build_request_without_super()

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_desc("TSCarAdmin", request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_inlines("TSCarAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_data("TSCarAdmin", [], 1, 10, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_save("TSCarAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_delete("TSCarAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.batch_model_save("TSCarAdmin", [], request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_action(
            Action(
                name="TSCarAdmin",
                action="test_action",
                search_condition=[],
                form_data={},
                input_data={},
            ),
            request,
        )
