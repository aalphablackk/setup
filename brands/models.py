from django.db import models
from django.conf import settings

# Create your models here.



class Brand(models.Model):

    class BrandType(models.TextChoices):
        PERSONAL = "personal", "Personal Brand"
        BUSINESS = "business", "Business"
        CREATOR = "creator", "Creator"
        FREELANCER = "freelancer", "Freelancer"
        STARTUP = "startup", "Startup"
        AGENCY = "agency", "Agency"
        ORGANIZATION = "organization", "Organization"
        OTHER = "other", "Other"

    class Goal(models.TextChoices):
        GROW_AUDIENCE = "grow_audience", "Grow my audience"
        BUILD_AUTHORITY = "build_authority", "Build authority"
        GET_CLIENTS = "get_clients", "Get clients"
        GENERATE_LEADS = "generate_leads", "Generate leads"
        SELL_PRODUCTS = "sell_products", "Sell products"
        PERSONAL_BRAND = "personal_brand", "Build a personal brand"
        ENGAGEMENT = "engagement", "Increase engagement"
        NOT_SURE = "not_sure", "I'm not sure yet"

    name = models.CharField(
        max_length=150
    )

    brand_type = models.CharField(
        max_length=30,
        choices=BrandType.choices,
    )

    industry = models.CharField(
        max_length=100,
        blank=True,
    )

    niche = models.CharField(
        max_length=100,
        blank=True,
    )


    primary_goal = models.CharField(
        max_length=40,
        choices=Goal.choices,
        blank=True,
    )


    target_audience = models.TextField(blank=True)
    platforms = models.TextField(blank=True)

    additional_information = models.TextField(
        blank=True,
        help_text=(
            "Tell Workbeam anything else about your brand, "
            "audience, story, products, personality or goals."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="brands",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    

class BrandKnowledge(models.Model):

    class Source(models.TextChoices):
        USER = "user", "User"
        AI = "ai", "AI"
        IMPORT = "import", "Import"
        WEBSITE = "website", "Website"
        SOCIAL = "social", "Social Media"

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="knowledge",
    )

    content = models.TextField()

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.USER,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.brand.name} knowledge"