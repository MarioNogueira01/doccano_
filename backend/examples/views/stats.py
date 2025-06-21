from datetime import datetime
import json

from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.permissions import IsProjectMember
from labels.models import Category
from label_types.models import CategoryType


class LabelVoteHistoryView(APIView):
    """Return aggregated vote counts per label."""
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get(self, request, project_id: int):
        qs = Category.objects.filter(example__project_id=project_id)

        # Optional dataset filter
        dataset_param = request.query_params.get("dataset")
        if dataset_param:
            qs = qs.filter(example__upload_name=dataset_param)

        # Optional perspective filters
        perspective_param = request.query_params.get("perspective_filters")
        if perspective_param:
            try:
                perspective_filters = json.loads(perspective_param)
                if perspective_filters:
                    # Esta é uma forma simplificada de filtrar. Pode precisar de ser ajustada
                    # para uma lógica mais complexa com Q objects se necessário.
                    for question_id, value in perspective_filters.items():
                        # Assume que o valor é único, não uma lista, para simplificar.
                        qs = qs.filter(
                            example__perspective_answers__perspective__id=question_id,
                            example__perspective_answers__answer=str(value)
                        )
            except (json.JSONDecodeError, AttributeError):
                pass  # Ignora filtros malformados

        # Map id -> text for faster lookup
        label_text_map = {
            obj.id: obj.text for obj in CategoryType.objects.filter(project_id=project_id)
        }

        # Build final aggregated counts
        cumulative = {}
        for cat in qs:
            cumulative[cat.label_id] = cumulative.get(cat.label_id, 0) + 1

        # Create a single, final snapshot object
        final_snapshot = self._snapshot_obj(qs.count(), cumulative, label_text_map)

        # The frontend expects a list, so wrap it
        return Response([final_snapshot] if final_snapshot else [])

    @staticmethod
    def _snapshot_obj(version: int, cum_dict: dict, label_map: dict):
        if not cum_dict:
            return None

        labels = []
        votes = []
        agreement = []
        
        total_votes = sum(cum_dict.values())

        for lid, cnt in cum_dict.items():
            labels.append(label_map.get(lid, str(lid)))
            votes.append(cnt)
            agreement.append((cnt / total_votes) * 100 if total_votes > 0 else 0)

        # O 'version' não é mais usado, mas mantemos a estrutura por consistência
        return {"version": version, "labels": labels, "votes": votes, "agreement": agreement} 