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
    """Return cumulative vote counts per label after each annotation ("versões").

    Query-parameters
    ----------------
    before : ISO-8601 datetime (opcional)
        Considere apenas anotações criadas até esta data.
    version : int (opcional)
        Snapshot até à N-ésima anotação.
    progress : int 0-100 (opcional)
        Snapshot correspondente a X % do total de anotações.
        Ignorado se "version" for fornecido.
    """

    permission_classes = [IsAuthenticated & IsProjectMember]

    def get(self, request, project_id: int):
        qs = Category.objects.filter(example__project_id=project_id).order_by("created_at", "id")

        # Optional dataset filter
        dataset_param = request.query_params.get("dataset")
        if dataset_param:
            qs = qs.filter(example__upload_name=dataset_param)

        # Optional perspective filters (JSON encoded)
        perspective_param = request.query_params.get("perspective_filters")
        if perspective_param:
            try:
                perspective_filters = json.loads(perspective_param)
            except json.JSONDecodeError:
                perspective_filters = None

            if perspective_filters:
                combined_q_filters = Q()
                has_any_filter = False

                for question_id, value in perspective_filters.items():
                    # Skip if empty list (no specific selection)
                    if isinstance(value, list) and len(value) == 0:
                        continue

                    has_any_filter = True

                    # Build answer filter for both example-level and project-level answers
                    if isinstance(value, list):
                        answers_list = [str(v) for v in value]
                        example_answer_q = Q(example__perspective_answers__answer__in=answers_list)
                        project_answer_q = Q(example__project__perspective_answers__answer__in=answers_list)
                    elif isinstance(value, bool):
                        answer_str = "Yes" if value else "No"
                        example_answer_q = Q(example__perspective_answers__answer=answer_str)
                        project_answer_q = Q(example__project__perspective_answers__answer=answer_str)
                    else:
                        answer_str = str(value)
                        example_answer_q = Q(example__perspective_answers__answer=answer_str)
                        project_answer_q = Q(example__project__perspective_answers__answer=answer_str)

                    current_q = (
                        (Q(example__perspective_answers__perspective__id=question_id) & example_answer_q) |
                        (Q(example__project__perspective_answers__perspective__id=question_id) & project_answer_q)
                    )
                    combined_q_filters &= current_q

                if has_any_filter:
                    qs = qs.filter(combined_q_filters).distinct()

        # ------------------------------------------------------------------
        # Agreement / Disagreement filter based on overall example status
        # overall_status can be "agreement" or "disagreement" (case-insensitive)
        # A status is considered "agreement" when the max percentage of any label
        # for a given example is >= threshold (default 70). Otherwise it's
        # considered "disagreement".
        # ------------------------------------------------------------------

        status_param = request.query_params.get("overall_status")
        if status_param:
            status_param = status_param.lower()
            if status_param in {"agreement", "disagreement"}:
                try:
                    threshold = int(request.query_params.get("threshold", 70))
                except ValueError:
                    threshold = 70

                # Aggregate counts per example and label
                agg = (
                    qs.values("example_id", "label_id")
                    .annotate(cnt=Count("id"))
                    .order_by()
                )

                example_totals = {}
                example_max = {}
                for row in agg:
                    eid = row["example_id"]
                    cnt = row["cnt"]
                    example_totals[eid] = example_totals.get(eid, 0) + cnt
                    example_max[eid] = max(example_max.get(eid, 0), cnt)

                matching_example_ids = []
                for eid in example_totals.keys():
                    total = example_totals[eid]
                    if total == 0:
                        continue
                    max_cnt = example_max[eid]
                    percentage = (max_cnt / total) * 100
                    is_discrepancy = percentage < threshold
                    status = "disagreement" if is_discrepancy else "agreement"
                    if status == status_param:
                        matching_example_ids.append(eid)

                # If no examples match, return empty response early
                if not matching_example_ids:
                    return Response([])

                qs = qs.filter(example_id__in=matching_example_ids)

        before_param = request.query_params.get("before")
        if before_param:
            try:
                before_dt = datetime.fromisoformat(before_param)
            except ValueError:
                return Response({"detail": "Invalid 'before' param"}, status=400)
            qs = qs.filter(created_at__lte=before_dt)

        total_annotations = qs.count()
        if total_annotations == 0:
            return Response([])

        # Map id -> text for faster lookup
        label_text_map = {
            obj.id: obj.text for obj in CategoryType.objects.filter(project_id=project_id)
        }

        # Apply version / progress filters (deterministic slice)
        version_param = request.query_params.get("version")
        progress_param = request.query_params.get("progress")
        if version_param is not None:
            try:
                version_n = int(version_param)
                if version_n < 1:
                    raise ValueError
            except ValueError:
                return Response({"detail": "version must be positive integer"}, status=400)
            qs = qs[:version_n]
        elif progress_param is not None:
            try:
                prog = int(progress_param)
                if not 0 <= prog <= 100:
                    raise ValueError
            except ValueError:
                return Response({"detail": "progress must be integer 0-100"}, status=400)
            slice_len = max(1, int(total_annotations * prog / 100))
            qs = qs[:slice_len]

        # Build cumulative counts
        cumulative = {}
        results = []
        version_counter = 0
        add_all_versions = version_param is None and progress_param is None

        for cat in qs:
            version_counter += 1
            cumulative[cat.label_id] = cumulative.get(cat.label_id, 0) + 1

            if add_all_versions:
                results.append(self._snapshot_obj(version_counter, cumulative, label_text_map))

        if not add_all_versions:
            results.append(self._snapshot_obj(version_counter, cumulative, label_text_map))

        return Response(results)

    @staticmethod
    def _snapshot_obj(version: int, cum_dict: dict, label_map: dict):
        labels = []
        votes = []
        for lid, cnt in cum_dict.items():
            labels.append(label_map.get(lid, str(lid)))
            votes.append(cnt)
        return {"version": version, "labels": labels, "votes": votes} 