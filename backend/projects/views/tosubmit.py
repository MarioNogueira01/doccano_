from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import ToSubmitQuestions, Project
from ..serializers import ToSubmitQuestionsSerializer

class ToSubmitQuestionsCreateView(APIView):
    permission_classes = [permissions.AllowAny]  # ou IsAuthenticated, se preferir

    def post(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Projeto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Se request.data for uma lista, adiciona project a cada item e usa many=True
        if isinstance(request.data, list):
            new_data = []
            for item in request.data:
                if not isinstance(item, dict):
                    return Response({'error': 'Cada item deve ser um objeto/dicionário.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                item['project'] = project.id
                new_data.append(item)
            serializer = ToSubmitQuestionsSerializer(data=new_data, many=True)
        else:
            data = request.data.copy()
            data['project'] = project.id
            serializer = ToSubmitQuestionsSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ToSubmitQuestionsListView(APIView):
    permission_classes = [permissions.AllowAny]  # ou IsAuthenticated, se preferir

    def get(self, request, project_id):
        questions = ToSubmitQuestions.objects.filter(project_id=project_id)
        serializer = ToSubmitQuestionsSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
