from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project, Version, DiscussionThread, DiscussionThreadMessage
from projects.serializers import DiscussionThreadSerializer, DiscussionThreadMessageSerializer
from projects.permissions import IsProjectMember


class DiscussionThreadListCreateView(APIView):
    """Lista threads de discussão (GET) ou cria uma nova (POST)."""
    permission_classes = [IsAuthenticated & IsProjectMember]

    def _get_current_version(self, project):
        return Version.objects.filter(project=project, status='open').order_by('-start_date').first()

    def get(self, request, project_id):
        version_id = request.query_params.get('version_id')
        project = get_object_or_404(Project, pk=project_id)

        if version_id:
            threads = DiscussionThread.objects.filter(project=project, version_id=version_id)
        else:
            # Apenas threads abertas e pertencentes à versão atual
            current_version = self._get_current_version(project)
            if current_version is not None:
                threads = DiscussionThread.objects.filter(project=project, closed=False, version=current_version)
            else:
                threads = DiscussionThread.objects.filter(project=project, closed=False, version__isnull=True)
        serializer = DiscussionThreadSerializer(threads, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.status == 'closed':
            return Response({'detail': 'Project is closed.'}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get('title')
        if not title or not title.strip():
            return Response({'detail': 'title is required.'}, status=status.HTTP_400_BAD_REQUEST)

        current_version = self._get_current_version(project)
        thread = DiscussionThread.objects.create(
            project=project,
            version=current_version,
            title=title.strip(),
            created_by=request.user,
        )
        serializer = DiscussionThreadSerializer(thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiscussionThreadMessageView(APIView):
    """Lista mensagens de um thread (GET) ou cria uma nova (POST)."""
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get(self, request, project_id, thread_id):
        thread = get_object_or_404(DiscussionThread, pk=thread_id, project_id=project_id)
        messages = DiscussionThreadMessage.objects.filter(thread=thread)
        serializer = DiscussionThreadMessageSerializer(messages, many=True)
        return Response({'messages': serializer.data})

    def post(self, request, project_id, thread_id):
        thread = get_object_or_404(DiscussionThread, pk=thread_id, project_id=project_id)
        if thread.closed or thread.project.status == 'closed':
            return Response({'detail': 'Thread is closed.'}, status=status.HTTP_400_BAD_REQUEST)

        message_text = request.data.get('message')
        if not message_text or not message_text.strip():
            return Response({'detail': 'message is required.'}, status=status.HTTP_400_BAD_REQUEST)

        msg = DiscussionThreadMessage.objects.create(
            thread=thread,
            message=message_text.strip(),
            created_by=request.user,
        )
        serializer = DiscussionThreadMessageSerializer(msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 