import abc
import uuid
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from polymorphic.models import PolymorphicModel

from roles.models import Role


class ProjectType(models.TextChoices):
    DOCUMENT_CLASSIFICATION = "DocumentClassification"
    SEQUENCE_LABELING = "SequenceLabeling"
    SEQ2SEQ = "Seq2seq"
    INTENT_DETECTION_AND_SLOT_FILLING = "IntentDetectionAndSlotFilling"
    SPEECH2TEXT = "Speech2text"
    IMAGE_CLASSIFICATION = "ImageClassification"
    BOUNDING_BOX = "BoundingBox"
    SEGMENTATION = "Segmentation"
    IMAGE_CAPTIONING = "ImageCaptioning"


class Project(PolymorphicModel):
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    guideline = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    project_type = models.CharField(max_length=30, choices=ProjectType.choices)
    random_order = models.BooleanField(default=False)
    collaborative_annotation = models.BooleanField(default=False)
    single_class_classification = models.BooleanField(default=False)
    allow_member_to_create_label_type = models.BooleanField(default=False)

    def add_admin(self):
        admin_role = Role.objects.get(name=settings.ROLE_PROJECT_ADMIN)
        Member.objects.create(
            project=self,
            user=self.created_by,
            role=admin_role,
        )

    @property
    @abc.abstractmethod
    def is_text_project(self) -> bool:
        return False

    def clone(self) -> "Project":
        """Clone the project.
        See https://docs.djangoproject.com/en/4.2/topics/db/queries/#copying-model-instances

        Returns:
            The cloned project.
        """
        project = Project.objects.get(pk=self.pk)
        project.pk = None
        project.id = None
        project._state.adding = True
        project.save()

        def bulk_clone(queryset: models.QuerySet, field_initializers: Optional[Dict[Any, Any]] = None):
            """Clone the queryset.

            Args:
                queryset: The queryset to clone.
                field_initializers: The field initializers.
            """
            if field_initializers is None:
                field_initializers = {}
            items = []
            for item in queryset:
                item.id = None
                item.pk = None
                for field, value_or_callable in field_initializers.items():
                    if callable(value_or_callable):
                        value_or_callable = value_or_callable()
                    setattr(item, field, value_or_callable)
                item.project = project
                item._state.adding = True
                items.append(item)
            queryset.model.objects.bulk_create(items)

        bulk_clone(self.role_mappings.all())
        bulk_clone(self.tags.all())

        # clone examples
        bulk_clone(self.examples.all(), field_initializers={"uuid": uuid.uuid4})

        # clone label types
        bulk_clone(self.categorytype_set.all())
        bulk_clone(self.spantype_set.all())
        bulk_clone(self.relationtype_set.all())

        return project

    def __str__(self):
        return self.name


class TextClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class SequenceLabelingProject(Project):
    allow_overlapping = models.BooleanField(default=False)
    grapheme_mode = models.BooleanField(default=False)
    use_relation = models.BooleanField(default=False)

    @property
    def is_text_project(self) -> bool:
        return True


class Seq2seqProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class IntentDetectionAndSlotFillingProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class Speech2textProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class BoundingBoxProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class SegmentationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageCaptioningProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class Tag(models.Model):
    text = models.TextField()
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="tags")

    def __str__(self):
        return self.text


class MemberManager(Manager):
    def can_update(self, project: int, member_id: int, new_role: str) -> bool:
        """The project needs at least 1 admin.

        Args:
            project: The project id.
            member_id: The member id.
            new_role: The new role name.

        Returns:
            Whether the mapping can be updated or not.
        """
        queryset = self.filter(project=project, role__name=settings.ROLE_PROJECT_ADMIN)
        if queryset.count() > 1:
            return True
        else:
            admin = queryset.first()
            # we can change the role except for the only admin.
            return admin.id != member_id or new_role == settings.ROLE_PROJECT_ADMIN

    def has_role(self, project_id: int, user: User, role_name: str):
        return self.filter(project=project_id, user=user, role__name=role_name).exists()


class Member(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="role_mappings")
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="role_mappings")
    role = models.ForeignKey(to=Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MemberManager()

    def clean(self):
        members = self.__class__.objects.exclude(id=self.id)
        if members.filter(user=self.user, project=self.project).exists():
            message = "This user is already assigned to a role in this project."
            raise ValidationError(message)

    def is_admin(self):
        return self.role.name == settings.ROLE_PROJECT_ADMIN

    @property
    def username(self):
        return self.user.username

    class Meta:
        unique_together = ("user", "project")




class PerspectiveGroup(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='perspective_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Perspective(models.Model):
    DATA_TYPES = [
        ('int', 'Integer'),
        ('string', 'String'),
        ('boolean', 'Boolean'),
    ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='perspectives')
    group = models.ForeignKey(
        'PerspectiveGroup',
        on_delete=models.CASCADE,
        related_name='questions',
        null=True
    )
    name = models.CharField(max_length=100)
    question = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    options = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = (('group', 'question'),)
        # ou, em versões mais recentes:
        # constraints = [
        #   models.UniqueConstraint(fields=['group','question'], name='unique_question_per_group')
        # ]

    def __str__(self):
        return f"{self.question} ({self.data_type})"


class PerspectiveAnswer(models.Model):
    perspective = models.ForeignKey(
        'Perspective', 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    project = models.ForeignKey(
        'Project', 
        on_delete=models.CASCADE, 
        related_name='perspective_answers'
    )
    example = models.ForeignKey(
        'examples.Example',
        on_delete=models.CASCADE,
        related_name='perspective_answers',
        null=True
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
    )
    answer = models.TextField()

    def __str__(self):

        return f"Answer to {self.perspective.question}: {self.answer}"


class ToSubmitQuestions(models.Model):
    project = models.ForeignKey(
        'Project', 
        on_delete=models.CASCADE, 
        related_name='discrepancies'
    )
    question = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='toSubmit')

    def __str__(self):
        return f"Discrepancy: {self.text}"
    

class VotingSession(models.Model):
    project = models.ForeignKey(
        'Project', 
        on_delete=models.CASCADE, 
        related_name='voting_sessions'
    )
    questions = models.JSONField(default=list, blank=True)  # Lista de strings
    created_at = models.DateTimeField(auto_now_add=True)
    vote_end_date = models.DateTimeField(null=True, blank=True)  # Definida depois
    finish = models.BooleanField(default=False)  # Novo campo boolean

    def __str__(self):
        return f"VotingSession for Project {self.project.id} created on {self.created_at}"
    
class VotingSessionAnswer(models.Model):
    voting_session = models.ForeignKey(
        'VotingSession', 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    project = models.ForeignKey(
        'Project', 
        on_delete=models.CASCADE, 
        related_name='voting_session_answers'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
    )
    answer = models.JSONField(default=list, blank=True)  # Lista de strings

    def __str__(self):
        return f"Answer to {self.voting_session.questions}: {self.answer}"

class RuleDiscussionMessage(models.Model):
    """Messages exchanged during discussion of a rule in a VotingSession."""
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='rule_messages'
    )
    voting_session = models.ForeignKey(
        'VotingSession',
        on_delete=models.CASCADE,
        related_name='rule_messages'
    )
    # Index of the question inside VotingSession.questions array. 0-based.
    question_index = models.PositiveIntegerField()

    message = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"RuleDiscussionMessage(session={self.voting_session.id}, idx={self.question_index})"

        return f"Answer for {self.perspective.question}: {self.answer}"

