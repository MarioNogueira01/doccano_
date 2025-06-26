from django.contrib import admin

from .models import (
    BoundingBoxProject,
    ImageCaptioningProject,
    ImageClassificationProject,
    Member,
    Project,
    SegmentationProject,
    Seq2seqProject,
    SequenceLabelingProject,
    Tag,
    TextClassificationProject,
    PerspectiveGroup,
    Perspective,
    PerspectiveAnswer,
    RuleDiscussionMessage,
    Version,
)


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "project",
    )
    ordering = ("user",)
    search_fields = ("user__username",)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "project_type", "random_order", "collaborative_annotation")
    ordering = ("project_type",)
    search_fields = ("name",)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "text",
    )
    ordering = (
        "project",
        "text",
    )
    search_fields = ("text",)


class VersionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "start_date",
        "end_date",
        "status",
        "duration_display"
    )
    list_filter = ("status", "start_date", "project")
    search_fields = ("project__name",)
    readonly_fields = ("start_date", "duration_display")
    ordering = ("-start_date",)

    def duration_display(self, obj):
        """Display duration in a human-readable format."""
        duration = obj.duration
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    duration_display.short_description = "Duration"


admin.site.register(Member, MemberAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TextClassificationProject, ProjectAdmin)
admin.site.register(SequenceLabelingProject, ProjectAdmin)
admin.site.register(Seq2seqProject, ProjectAdmin)
admin.site.register(BoundingBoxProject, ProjectAdmin)
admin.site.register(SegmentationProject, ProjectAdmin)
admin.site.register(ImageCaptioningProject, ProjectAdmin)
admin.site.register(ImageClassificationProject, ProjectAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(PerspectiveGroup)
admin.site.register(Perspective)
admin.site.register(PerspectiveAnswer)
admin.site.register(RuleDiscussionMessage)
admin.site.register(Version, VersionAdmin)

