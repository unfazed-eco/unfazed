import typing as t

from pydantic import BaseModel, Field

from unfazed.schema import Condition
from unfazed.type import Doc

ModelLineDataT: t.TypeAlias = t.Dict[str, t.Any]


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
    search_condition: t.List[Condition] = Field(
        default_factory=list,
        description="conditions to filter the data",
        examples=[
            {
                "field": "name",
                "eq": "admin",
            },
        ],
    )

    form_data: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="form data for the action",
    )

    input_data: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="input data for the action",
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


class Delete(BaseModel):
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

    strategy: t.Literal["set_null", "delete", "do_nothing"] = Field(
        default="do_nothing",
        description="strategy to delete the related data",
        examples=[
            "set_null",
            "delete",
            "do_nothing",
        ],
    )
