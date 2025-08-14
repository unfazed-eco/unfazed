import typing as t

from pydantic import BaseModel, Field

T = t.TypeVar("T", bound=BaseModel)


class Result[T](BaseModel):
    count: int = Field(description="total number of items")
    data: t.List[T] = Field(description="list of items")


class Through(BaseModel):
    """

    Example:
        User ←→ UserRole ←→ Role
        - User.id ←→ UserRole.user_id (source_to_through)
        - Role.id ←→ UserRole.role_id (target_to_through)
    """

    mid_model: str = Field(description="through model name")

    # 源模型到中间表的字段映射
    source_field: str = Field(description="source field name")
    source_to_through_field: str = Field(description="source to through field name")

    # 目标模型到中间表的字段映射
    target_field: str = Field(description="target field name")
    target_to_through_field: str = Field(description="target to through field name")


class Relation(BaseModel):
    """
    Model relationship description, supports field mapping for various relationship types.

    Relationship type explanation:
    - fk: ForeignKey relationship - many-to-one
    - o2o: OneToOne relationship
    - m2m: ManyToMany relationship - may require a through table
    - bk_fk: Backward ForeignKey relationship - one-to-many
    - bk_o2o: Backward OneToOne relationship
    """

    to: str = Field(description="Target model name (e.g., 'UserSerializer')")

    # Source model field info
    source_field: str = Field(
        description="Related field name in the source model (e.g., 'user_id', 'role')"
    )

    # Target model field info
    dest_field: str = Field(
        description="Corresponding field name in the target model (usually the primary key, e.g., 'id')"
    )

    # Relationship type
    relation: t.Literal["m2m", "fk", "o2o", "bk_fk", "bk_o2o"] = Field(
        description="Relationship type: m2m=ManyToMany, fk=ForeignKey, o2o=OneToOne, bk_fk=Backward ForeignKey, bk_o2o=Backward OneToOne"
    )

    # Through table info (only for m2m relationships)
    through: t.Optional[Through] = Field(
        default=None,
        description="Mapping info for the through table in many-to-many relationships, only used when relation='m2m'",
    )
