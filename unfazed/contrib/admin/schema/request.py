import typing as t

from pydantic import BaseModel, Field

from unfazed.schema import Condition
from unfazed.type import Doc

ModelLineDataT = t.TypeVar("ModelLineDataT", bound=t.Dict[str, t.Any])


class Detail(BaseModel):
    name: str = Field(description="name of the model")
    data: ModelLineDataT = Field(
        description="one line data of the model",
        examples=[
            {
                "id": 1,
                "name": "admin",
            }
        ],
    )


class Data(BaseModel):
    cond: t.List[Condition] = Field(
        default_factory=list,
        description="conditions to filter the data",
        examples=[
            {
                "field": "name",
                "eq": "admin",
            },
            {
                "field": "age",
                "gt": 18,
            },
        ],
    )
    name: str = Field(description="name of the model")
    page: int = Field(description="page number")
    size: int = Field(description="page size")


class Action(BaseModel):
    name: str = Field(description="name of the model")
    action: str = Field(description="action of the action")
    data: t.Dict[str, t.Any] = Field(
        description="one line data of the model",
        examples=[
            {
                "id": 1,
                "name": "admin",
            }
        ],
    )


class Save(BaseModel):
    name: str = Field(description="name of the model")
    data: t.Annotated[
        ModelLineDataT,
        Doc(
            description="depends on the tortoise model, use unfazed.contrib.auth.models.User as example",
            examples=[
                {
                    "id": 1,
                    "username": "admin",
                    "email": "",
                    "created_at": 12345,
                    "updated_at": 12345,
                }
            ],
        ),
    ]
    inlines: t.Annotated[
        t.Dict[str, t.List[ModelLineDataT]],
        Doc(
            description="relation model to `data`, use unfazed.contrib.auth.models.Group as example",
            examples=[
                {
                    "groups": [
                        {"name": "group1", "id": 1},
                        {"name": "group2", "id": 2},
                    ],
                    "roles": [{"name": "role1", "id": 1}, {"name": "role2", "id": 2}],
                }
            ],
        ),
    ]


class Delete(BaseModel):
    name: str = Field(description="name of the model")
    data: t.List[ModelLineDataT] = Field(
        description="one line data of the model",
        examples=[
            {
                "id": 1,
                "name": "admin",
            }
        ],
    )
