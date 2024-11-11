import typing as t

from pydantic import BaseModel

from unfazed.schema import Condtion
from unfazed.type import Doc


class Detail(BaseModel):
    name: str
    data: t.Dict[str, t.Any]


class Data(BaseModel):
    cond: t.List[Condtion | None]
    name: str
    page: int
    size: int


class Action(BaseModel):
    name: str
    action: str
    data: t.Dict[str, t.Any]


class Save(BaseModel):
    name: str
    data: t.Annotated[
        t.Dict[str, t.Any],
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
        t.Dict[str, t.List[t.Dict[str, t.Any]]],
        Doc(
            description="relation model to `data`, use unfazed.contrib.auth.models.Group as example",
            examples={
                "groups": [{"name": "group1", "id": 1}, {"name": "group2", "id": 2}],
                "roles": [{"name": "role1", "id": 1}, {"name": "role2", "id": 2}],
            },
        ),
    ]


class Delete(BaseModel):
    name: str
    data: t.Dict[str, t.Any]
