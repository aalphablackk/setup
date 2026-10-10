from django.test import override_settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from brands.models import Brand, BrandKnowledge


User = get_user_model()

# Create your tests here.

@override_settings(LOGIN_URL="/accounts/login/")
class BrandBrainTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="brand_tester",
            password="test-password",
        )

        self.other_user = User.objects.create_user(
            username="other_tester",
            password="test-password",
        )

        self.brand = Brand.objects.create(
            name="Test Brand",
            brand_type=Brand.BrandType.BUSINESS,
            industry="technology",
            niche="Business automation",
            primary_goal=Brand.Goal.GET_CLIENTS,
            created_by=self.user,
        )

    def test_brand_creation_and_defaults(self):
        brand = Brand.objects.create(
            name="Second Brand",
            brand_type=Brand.BrandType.CREATOR,
            created_by=self.user,
        )

        self.assertTrue(brand.is_active)
        self.assertEqual(brand.target_audience, "")
        self.assertEqual(brand.platforms, "")

    def test_brand_list_requires_login(self):
        response = self.client.get(reverse("brands:list"))

        self.assertEqual(response.status_code, 302)

    def test_brand_list_shows_only_users_active_brands(self):
        self.client.force_login(self.user)

        Brand.objects.create(
            name="Other User Brand",
            brand_type=Brand.BrandType.PERSONAL,
            created_by=self.other_user,
        )

        inactive_brand = Brand.objects.create(
            name="Inactive Brand",
            brand_type=Brand.BrandType.BUSINESS,
            created_by=self.user,
            is_active=False,
        )

        response = self.client.get(reverse("brands:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.brand.name)
        self.assertNotContains(response, "Other User Brand")
        self.assertNotContains(response, inactive_brand.name)

    def test_brand_detail_is_private_to_owner(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("brands:detail", args=[self.brand.pk])
        )

        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("brands:detail", args=[self.brand.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_brand_update_changes_existing_brand(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("brands:update", args=[self.brand.pk]),
            {
                "name": "Updated Test Brand",
                "brand_type": Brand.BrandType.BUSINESS,
                "industry": "technology",
                "niche": "AI tools",
                "primary_goal": Brand.Goal.GET_CLIENTS,
                "target_audience": ["Businesses", "Entrepreneurs"],
                "platforms": ["LinkedIn"],
                "additional_information": "Updated details",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.brand.refresh_from_db()

        self.assertEqual(self.brand.name, "Updated Test Brand")
        self.assertEqual(self.brand.niche, "AI tools")
        self.assertEqual(
            self.brand.target_audience,
            "Businesses, Entrepreneurs",
        )
        self.assertEqual(self.brand.platforms, "LinkedIn")

    def test_brand_knowledge_can_be_saved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("brands:knowledge_save", args=[self.brand.pk]),
            {
                "knowledge_type": BrandKnowledge.KnowledgeType.VOICE,
                "content": "Clear, helpful, and practical.",
            },
        )

        self.assertEqual(response.status_code, 302)

        knowledge = BrandKnowledge.objects.get(brand=self.brand)

        self.assertEqual(
            knowledge.knowledge_type,
            BrandKnowledge.KnowledgeType.VOICE,
        )
        self.assertEqual(
            knowledge.content,
            "Clear, helpful, and practical.",
        )
        self.assertEqual(
            knowledge.source,
            BrandKnowledge.Source.USER,
        )

    def test_cannot_add_knowledge_to_another_users_brand(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("brands:knowledge_save", args=[self.brand.pk]),
            {
                "knowledge_type": BrandKnowledge.KnowledgeType.STORY,
                "content": "Unauthorized update",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            BrandKnowledge.objects.filter(
                brand=self.brand,
                content="Unauthorized update",
            ).exists()
        )
