from django.contrib import admin
from .models import Brand, BrandKnowledge

# Register your models here.




@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "brand_type",
        "industry",
        "niche",
        "primary_goal",
        "created_by",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "brand_type",
        "primary_goal",
        "is_active",
    )

    search_fields = (
        "name",
        "industry",
        "niche",
        "additional_information",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(BrandKnowledge)
class BrandKnowledgeAdmin(admin.ModelAdmin):
    list_display = (
        "brand",
        "knowledge_type",
        "source",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "knowledge_type",
        "source",
        "is_active",
    )

    search_fields = (
        "brand__name",
        "content",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )