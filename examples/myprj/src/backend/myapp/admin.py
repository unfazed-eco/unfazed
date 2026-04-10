from unfazed.contrib.admin.registry import (
    ActionKwargs,
    ActionOutput,
    AdminRelation,
    AdminThrough,
    ModelAdmin,
    ModelInlineAdmin,
    CustomAdmin,
    action,
    register,
)
from unfazed.contrib.admin.registry.models import CustomField
from unfazed.contrib.common.schema import BaseResponse

from . import serializers as s


@register(s.StudentSerializer)
class StudentAdmin(ModelAdmin):
    inlines = [
        AdminRelation(
            target="CourseAdmin",
            relation="m2m",
            through=AdminThrough(
                through="StudentCourseAdmin",
                source_field="id",
                source_to_through_field="student_id",
                target_field="id",
                target_to_through_field="course_id",
            ),
        ),
        AdminRelation(target="BookAdmin"),
        AdminRelation(target="ProfileAdmin"),
    ]


@register(s.CourseSerializer)
class CourseAdmin(ModelInlineAdmin):
    pass


@register(s.StudentCourseSerializer)
class StudentCourseAdmin(ModelInlineAdmin):
    pass


@register(s.BookSerializer)
class BookAdmin(ModelInlineAdmin):
    pass


@register(s.ProfileSerializer)
class ProfileAdmin(ModelInlineAdmin):
    pass


@register()
class BookSerializer(CustomAdmin):
    fields_set = [
        CustomField(name="id", label="ID", type="number"),
        CustomField(name="name", label="Name", type="text"),
        CustomField(name="owner", label="Owner", type="text"),
    ]

    @action(
        name="get_owner",
        label="Get Owner",
        description="Get owner of the book",
        confirm=True,
        output=ActionOutput.Display,
    )
    async def get_owner(self, ctx: ActionKwargs) -> BaseResponse:
        return BaseResponse[dict](data={"message": "Owner retrieved successfully"})
