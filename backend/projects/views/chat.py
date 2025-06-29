from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from projects.models import ProjectDiscussionMessage, Version
from projects.serializers import ProjectDiscussionSerializer

chat_messages = {}  # Dictionary to store messages by project

class ChatMessagesView(APIView):
    """
    API endpoint para mensagens de chat globais de um projeto.
    As mensagens ficam associadas à versão atualmente "open" do projeto.
    """
    permission_classes = [IsAuthenticated]

    def _get_current_version(self, project_id):
        """Obtém a versão atual (status='open') do projeto."""
        try:
            return Version.objects.get(project_id=project_id, status='open')
        except Version.DoesNotExist:
            # Como fallback, retorna a versão mais recente
            return Version.objects.filter(project_id=project_id).order_by('-start_date').first()

    def get(self, request, project_id):
        version_id_param = request.query_params.get('version_id')
        if version_id_param is not None:
            try:
                version = Version.objects.get(id=version_id_param, project_id=project_id)
            except Version.DoesNotExist:
                return Response({'detail': 'Version not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            version = self._get_current_version(project_id)
            if version is None:
                return Response([], status=status.HTTP_200_OK)

        queryset = ProjectDiscussionMessage.objects.filter(project_id=project_id, version=version)
        serializer = ProjectDiscussionSerializer(queryset.order_by('created_at'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        version = self._get_current_version(project_id)
        if version is None:
            return Response({'detail': 'Project version not found.'}, status=status.HTTP_400_BAD_REQUEST)

        message_text = request.data.get('message')
        if not message_text or not message_text.strip():
            return Response({'detail': 'message field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        msg_obj = ProjectDiscussionMessage.objects.create(
            project_id=project_id,
            version=version,
            message=message_text.strip(),
            created_by=request.user
        )
        serializer = ProjectDiscussionSerializer(msg_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)