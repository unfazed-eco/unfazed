from unfazed.contrib.admin.registry import (
    AdminRelation,
    AdminThrough,
    ModelAdmin,
    ModelInlineAdmin,
    register,
)

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
