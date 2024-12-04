from unfazed.serializer.tortoise import TSerializer

from .models import Book, Group, Profile, User


class UserSerializer(TSerializer):
    class Meta:
        model = User


class GroupSerializer(TSerializer):
    class Meta:
        model = Group


class BookSerializer(TSerializer):
    class Meta:
        model = Book


class ProfileSerializer(TSerializer):
    class Meta:
        model = Profile
