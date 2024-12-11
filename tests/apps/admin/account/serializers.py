from unfazed.serializer import Serializer

from .models import Book, Group, Profile, User


class UserSerializer(Serializer):
    class Meta:
        model = User


class GroupSerializer(Serializer):
    class Meta:
        model = Group


class BookSerializer(Serializer):
    class Meta:
        model = Book


class ProfileSerializer(Serializer):
    class Meta:
        model = Profile
