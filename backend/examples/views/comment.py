from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from examples.models import Comment, Example
from examples.permissions import IsOwnComment
from examples.serializers import CommentSerializer
from projects.permissions import IsProjectMember
from projects.models import Project


class CommentList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated & IsProjectMember]
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ["example"]
    search_fields = ("text",)
    ordering_fields = ("created_at", "example")

    def get_queryset(self):
        queryset = Comment.objects.filter(example__project_id=self.kwargs["project_id"])
        version_param = self.request.query_params.get("version")
        label_param = self.request.query_params.get("label")
        if label_param is not None:
            queryset = queryset.filter(label=label_param)
        if version_param is not None:
            queryset = queryset.filter(project_version=version_param)
        else:
            # Se não for especificada versão, usar a versão actual do projecto
            current_version = queryset.first().example.project.project_version if queryset.exists() else 1
            queryset = queryset.filter(project_version=current_version)
        return queryset

    def perform_create(self, serializer):
        example_id = self.request.query_params.get("example")
        version_param = self.request.query_params.get("version")

        if version_param is not None:
            project_version = int(version_param)
        else:
            try:
                ex = Example.objects.get(pk=example_id)
                project_version = ex.project.project_version
            except Exception:
                project_version = 1

        serializer.save(
            example_id=example_id,
            user=self.request.user,
            label=self.request.query_params.get("label"),
            project_version=project_version,
        )

    def delete(self, request, *args, **kwargs):
        delete_ids = request.data["ids"]
        Comment.objects.filter(user=request.user, pk__in=delete_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated & IsProjectMember & IsOwnComment]
