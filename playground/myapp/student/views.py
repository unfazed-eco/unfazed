import typing as t

from unfazed.http import HttpRequest, JsonResponse

from . import schema as S


async def list_student(
    request: HttpRequest, ctx: S.StudentQuery
) -> t.Annotated[JsonResponse[S.StudentResponse], S.StudentResponseMeta]:
    students = []
    for i in range(10):
        students.append(
            S.Student(name=f"Student {i}", age=i, email=f"email_{i}@gmail.com")
        )

    return JsonResponse(S.StudentResponse(count=10, data=students))
