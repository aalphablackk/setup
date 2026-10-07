from django.contrib import admin

# Register your models here.

from .models import (
    ResearchFinding,
    ResearchItem,
    ResearchSession,
    ResearchSource,
    ResearchRun,
    ResearchRunItem,
)


@admin.register(ResearchSession)
class ResearchSessionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "brand",
        "mode",
        "status",
        "updated_at",
    )

    list_filter = (
        "mode",
        "status",
    )

    search_fields = (
        "title",
        "research_brief",
        "brand__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ResearchSource)
class ResearchSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "source_type",
        "session",
        "created_at",
    )

    list_filter = (
        "source_type",
    )

    search_fields = (
        "name",
        "url",
        "session__title",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(ResearchItem)
class ResearchItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "source",
        "published_at",
        "collected_at",
    )

    search_fields = (
        "title",
        "url",
        "raw_content",
        "source__name",
    )

    readonly_fields = (
        "collected_at",
    )


@admin.register(ResearchFinding)
class ResearchFindingAdmin(admin.ModelAdmin):
    list_display = (
        "topic",
        "finding_type",
        "confidence",
        "session",
        "created_at",
    )

    list_filter = (
        "finding_type",
        "confidence",
    )

    search_fields = (
        "topic",
        "finding",
        "audience",
        "evidence",
        "session__title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
@admin.register(ResearchRun)
class ResearchRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "status",
        "search_count",
        "result_count",
        "created_at",
        "completed_at",
    )

    list_filter = ("status",)

    search_fields = (
        "session__title",
        "error_message",
    )

    readonly_fields = (
        "created_at",
        "started_at",
        "completed_at",
    )
@admin.register(ResearchRunItem)
class ResearchRunItemAdmin(admin.ModelAdmin):
    list_display = ("run", "item", "created_at")
    search_fields = (
        "run__session__title",
        "item__title",
    )
    readonly_fields = ("created_at",)