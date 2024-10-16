from unfazed.route import path

from .views import list_student

patterns = [
    path("/student-list", endpoint=list_student, methods=["GET"]),
]
