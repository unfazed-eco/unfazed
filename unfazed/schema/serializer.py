import typing as t

from pydantic import BaseModel, Field

T = t.TypeVar("T", bound=BaseModel)


class Result[T](BaseModel):
    count: int = Field(description="total number of items")
    data: t.List[T] = Field(description="list of items")


class Relation(BaseModel):
    """
    Model relationship description, supports field mapping for various relationship types.

    Relationship type explanation:
    - fk: ForeignKey relationship - many-to-one
    - o2o: OneToOne relationship
    - m2m: ManyToMany relationship - may require a through table
    - bk_fk: Backward ForeignKey relationship - one-to-many
    - bk_o2o: Backward OneToOne relationship

    Usage:

    ```python
    class UserSerializer(BaseSerializer):
        id = IntegerField()
        name = CharField()

    class UserRoleSerializer(BaseSerializer):
        id = IntegerField()
        user_id = IntegerField()
        role_id = IntegerField()

    class RoleSerializer(BaseSerializer):
        id = IntegerField()
        name = CharField()

    class ProfileSerializer(BaseSerializer):
        id = IntegerField()
        name = CharField()
        user_id = IntegerField()

    class BookSerializer(BaseSerializer):
        id = IntegerField()
        name = CharField()
        author_id = IntegerField()


    def main():

        relation_user_to_role = Relation(
            target="RoleSerializer",
            source_field="",
            target_field="",
            relation="m2m",
            through=Through(
                through="UserRoleSerializer",
                source_field="id",
                source_to_through_field="user_id",
                target_field="id",
                target_to_through_field="role_id",
            ),
        )

        relation_book_to_user = Relation(
            target="UserSerializer",
            source_field="author_id",
            target_field="id",
            relation="fk",
        )

        relation_profile_to_user = Relation(
            target="UserSerializer",
            source_field="user_id",
            target_field="id",
            relation="o2o",
        )

    ```
    """

    target: str = Field(description="Target Serializer name (e.g., 'UserSerializer')")

    # Source model field info
    source_field: t.Optional[str] = Field(
        default=None,
        description="Related field name in the source Serializer (e.g., 'user_id', 'role')",
    )

    # Target model field info
    target_field: t.Optional[str] = Field(
        default=None,
        description="Corresponding field name in the target Serializer (usually the primary key, e.g., 'id')",
    )

    # Relationship type
    relation: t.Literal["m2m", "fk", "o2o", "bk_fk", "bk_o2o"] = Field(
        description="Relationship type: m2m=ManyToMany, fk=ForeignKey, o2o=OneToOne, bk_fk=Backward ForeignKey, bk_o2o=Backward OneToOne"
    )
