from pydantic import BaseModel, Field


class Command(BaseModel):
    path: str = Field(
        ...,
        description="Path to the command which can be imported",
        examples=["unfazed.command.BaseCommand"],
    )
    stem: str = Field(
        ...,
        description="Stem name of the command",
        examples=["startapp"],
    )
    label: str = Field(
        ...,
        description="Label of the command",
        examples=["unfazed.command.internal"],
    )
