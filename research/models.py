from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from brands.models import Brand

# Create your models here.

class ResearchSession(models.Model):
    class Mode(models.TextChoices):
        CONNECTED = "connected", "Connected to Brand"
        INDEPENDENT = "independent", "Independent Research"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        RESEARCHING = "researching", "Researching"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Depth(models.TextChoices):
        QUICK = "quick", "Quick"
        STANDARD = "standard", "Standard"
        DEEP = "deep", "Deep"

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="research_sessions",
        null=True,
        blank=True,
    )

    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.INDEPENDENT,
    )

    title = models.CharField(max_length=200)

    research_brief = models.TextField(
        help_text="Describe what you want Workbeam to research.",
    )

    summary = models.TextField(blank=True)
    
    depth = models.CharField(
        max_length=20,
        choices=Depth.choices,
        default=Depth.STANDARD,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="research_sessions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class ResearchSource(models.Model):
    class SourceType(models.TextChoices):
        WEB = "web", "Web"
        INSTAGRAM = "instagram", "Instagram"
        TIKTOK = "tiktok", "TikTok"
        LINKEDIN = "linkedin", "LinkedIn"

    session = models.ForeignKey(
        ResearchSession,
        on_delete=models.CASCADE,
        related_name="sources",
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
    )

    name = models.CharField(max_length=255, blank=True)

    url = models.URLField(
        blank=True,
        max_length=1000,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_source_type_display()} — {self.name or 'Source'}"


class ResearchItem(models.Model):
    source = models.ForeignKey(
        ResearchSource,
        on_delete=models.CASCADE,
        related_name="items",
    )

    title = models.CharField(
        max_length=500,
        blank=True,
    )

    url = models.URLField(
        blank=True,
        max_length=1000,
    )

    raw_content = models.TextField(
        blank=True,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    collected_at = models.DateTimeField(
        auto_now_add=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-collected_at"]

    def __str__(self):
        return self.title or self.url or f"Research item #{self.pk}"


class ResearchFinding(models.Model):
    class FindingType(models.TextChoices):
        TOPIC = "topic", "Topic"
        PROBLEM = "problem", "Problem"
        QUESTION = "question", "Question"
        TREND = "trend", "Trend"
        DESIRE = "desire", "Desire"
        OBJECTION = "objection", "Objection"
        COMPETITOR_ACTIVITY = "competitor_activity", "Competitor Activity"
        CONTENT_PATTERN = "content_pattern", "Content Pattern"
        AUDIENCE_INSIGHT = "audience_insight", "Audience Insight"
        OPPORTUNITY_SIGNAL = "opportunity_signal", "Opportunity Signal"

    class Confidence(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    session = models.ForeignKey(
        ResearchSession,
        on_delete=models.CASCADE,
        related_name="findings",
    )

    research_item = models.ForeignKey(
        ResearchItem,
        on_delete=models.SET_NULL,
        related_name="findings",
        null=True,
        blank=True,
    )

    finding_type = models.CharField(
        max_length=40,
        choices=FindingType.choices,
    )

    topic = models.CharField(
        max_length=255,
        blank=True,
    )

    finding = models.TextField()

    audience = models.TextField(blank=True)

    why_it_matters = models.TextField(blank=True)

    limitations = models.TextField(blank=True)

    related_questions = models.JSONField(
        default=list,
        blank=True,
    )

    content_opportunities = models.JSONField(
        default=list,
        blank=True,
    )

    evidence = models.TextField(blank=True)

    confidence = models.CharField(
        max_length=10,
        choices=Confidence.choices,
        default=Confidence.MEDIUM,
    )

    audience = models.TextField(
        blank=True,
    )

    evidence = models.TextField(
        blank=True,
    )

    confidence = models.CharField(
        max_length=10,
        choices=Confidence.choices,
        default=Confidence.MEDIUM,
    )
    run = models.ForeignKey(
        "ResearchRun",
        on_delete=models.CASCADE,
        related_name="findings",
        null=True,
        blank=True,
    )
    importance = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_finding_type_display()} — {self.topic or 'Finding'}"


class ResearchRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Stage(models.TextChoices):
        PLANNING = "planning", "Planning research"
        SEARCHING = "searching", "Searching"
        COLLECTING = "collecting", "Collecting evidence"
        ANALYZING = "analyzing", "Analyzing evidence"
        BUILDING = "building", "Building intelligence"
        COMPLETED = "completed", "Research complete"
        FAILED = "failed", "Research failed"


    stage = models.CharField(
        max_length=20,
        choices=Stage.choices,
        default=Stage.PLANNING,
    )

    stage_message = models.CharField(
        max_length=255,
        blank=True,
    )
    session = models.ForeignKey(
        ResearchSession,
        on_delete=models.CASCADE,
        related_name="runs",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    queries = models.JSONField(default=list, blank=True)

    search_count = models.PositiveIntegerField(default=0)

    result_count = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True)

    started_at = models.DateTimeField(null=True, blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.session.title} — Run {self.pk}"

class ResearchRunItem(models.Model):
    run = models.ForeignKey(
        ResearchRun,
        on_delete=models.CASCADE,
        related_name="run_items",
    )
    item = models.ForeignKey(
        ResearchItem,
        on_delete=models.CASCADE,
        related_name="research_runs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["run", "item"],
                name="unique_research_run_item",
            )
        ]

    def __str__(self):
        return f"Run {self.run_id} — {self.item.title}"