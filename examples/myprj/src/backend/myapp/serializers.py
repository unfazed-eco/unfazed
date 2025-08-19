from unfazed.serializer import Serializer

from . import models as m


class StudentSerializer(Serializer):
    class Meta:
        model = m.Student


class CourseSerializer(Serializer):
    class Meta:
        model = m.Course


class StudentCourseSerializer(Serializer):
    class Meta:
        model = m.StudentCourse


class BookSerializer(Serializer):
    class Meta:
        model = m.Book


class ProfileSerializer(Serializer):
    class Meta:
        model = m.Profile
