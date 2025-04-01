from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.perspective import PerspectiveQuestionViewSet, PerspectiveViewSet
from .views.project import ProjectList, ProjectDetail, CloneProject
from .views.tag import TagList, TagDetail
from .views.member import MemberList, MemberDetail, MyRole
from projects.views.perspective import PerspectiveAnswerViewSet

router = DefaultRouter()

urlpatterns = [
    path("projects", ProjectList.as_view(), name="project_list"),
    path("projects/<int:project_id>", ProjectDetail.as_view(), name="project_detail"),
    path("projects/<int:project_id>/my-role", MyRole.as_view(), name="my_role"),
    path("projects/<int:project_id>/tags", TagList.as_view(), name="tag_list"),
    path("projects/<int:project_id>/tags/<int:tag_id>", TagDetail.as_view(), name="tag_detail"),
    path("projects/<int:project_id>/members", MemberList.as_view(), name="member_list"),
    path("projects/<int:project_id>/members/<int:member_id>", MemberDetail.as_view(), name="member_detail"),
    path("projects/<int:project_id>/clone", CloneProject.as_view(), name="clone_project"),

    # Rota para PerspectiveViewSet
    path(
        "projects/<int:project_id>/perspectives/",
        PerspectiveViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="perspective-list-create"
    ),

    path(
        "projects/<int:project_id>/perspectives/<int:perspective_id>/questions/",
        PerspectiveQuestionViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="perspectivequestion-list-create"
    ),

    path(
        "projects/<int:project_id>/perspectivesanswers/",
        PerspectiveAnswerViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="perspectiveanswer-list-create"
    ),
]
