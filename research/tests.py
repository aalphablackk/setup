
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from research.models import (
    ResearchItem,
    ResearchRun,
    ResearchRunItem,
    ResearchSession,
    ResearchSource,
)
from research.services.run import ResearchRunService
from research.services.web import WebResearchService

# Create your tests here.

User = get_user_model()


@override_settings(TAVILY_API_KEY="test-key")
class WebResearchServiceTests(TestCase):
    """Test collection limits without making external API calls."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="research_tester",
            password="test-password",
        )

        self.session = ResearchSession.objects.create(
            created_by=self.user,
            title="Test research",
            research_brief="Understand audience needs.",
            depth=ResearchSession.Depth.STANDARD,
        )

        self.source = ResearchSource.objects.create(
            session=self.session,
            source_type="web",
            name="Web research",
        )

        self.run = ResearchRun.objects.create(
            session=self.session,
            depth=self.session.depth,
            status=ResearchRun.Status.RUNNING,
        )

    @patch("research.services.web.TavilyClient")
    @patch("research.services.web.ResearchPlanner")
    def test_depth_limits(self, planner_class, tavily_class):
        cases = [
            ("quick", 2, 3),
            ("standard", 5, 5),
            ("deep", 8, 5),
        ]

        service = WebResearchService()
        service.search = lambda query, max_results=5: [
            {
                "title": f"Result {query}-{i}",
                "url": f"https://example.com/{query}/{i}",
                "raw_content": "Test research content",
                "published_at": None,
                "metadata": {},
            }
            for i in range(max_results)
        ]

        for depth, max_queries, results_per_query in cases:
            with self.subTest(depth=depth):
                self.session.depth = depth
                self.session.save(update_fields=["depth"])

                planner = planner_class.return_value
                planner.plan.return_value = [
                    f"query-{i}" for i in range(10)
                ]

                run = ResearchRun.objects.create(
                    session=self.session,
                    depth=depth,
                    status=ResearchRun.Status.RUNNING,
                )

                items = service.collect_for_session(
                    session=self.session,
                    run=run,
                )

                self.assertEqual(run.search_count, max_queries)
                self.assertEqual(
                    len(items),
                    max_queries * results_per_query,
                )
                self.assertEqual(
                    run.result_count,
                    max_queries * results_per_query,
                )

                run.delete()

    @patch("research.services.web.TavilyClient")
    @patch("research.services.web.ResearchPlanner")
    def test_duplicate_urls_are_not_collected_twice(
        self, planner_class, tavily_class
    ):
        planner_class.return_value.plan.return_value = [
            "first query",
            "second query",
        ]

        service = WebResearchService()
        service.search = lambda query, max_results=5: [
            {
                "title": "Same result",
                "url": "https://example.com/shared",
                "raw_content": "Shared content",
                "published_at": None,
                "metadata": {},
            }
        ]

        items = service.collect_for_session(
            session=self.session,
            run=self.run,
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(
            ResearchRunItem.objects.filter(run=self.run).count(),
            1,
        )

    @patch("research.services.web.TavilyClient")
    @patch("research.services.web.ResearchPlanner")
    def test_missing_web_source_raises_error(
        self, planner_class, tavily_class
    ):
        self.source.delete()

        service = WebResearchService()

        with self.assertRaisesMessage(
            ValueError,
            "No Web research source has been added",
        ):
            service.collect_for_session(
                session=self.session,
                run=self.run,
            )


class ResearchRunServiceTests(TestCase):
    """Test run orchestration with collection and analysis mocked."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="run_tester",
            password="test-password",
        )

        self.session = ResearchSession.objects.create(
            created_by=self.user,
            title="Run service test",
            research_brief="Test research execution.",
            depth=ResearchSession.Depth.QUICK,
        )

    @patch("research.services.run.ResearchAnalyzer")
    @patch("research.services.run.WebResearchService")
    def test_successful_run_records_depth_and_completes(
        self, web_service_class, analyzer_class
    ):
        web_service_class.return_value.collect_for_session.return_value = []

        analyzer_class.return_value.analyze.return_value = {
            "summary": "Research completed successfully.",
            "findings": [],
        }

        run = ResearchRunService().execute(self.session)

        self.session.refresh_from_db()
        run.refresh_from_db()

        self.assertEqual(run.depth, ResearchSession.Depth.QUICK)
        self.assertEqual(run.status, ResearchRun.Status.COMPLETED)
        self.assertEqual(self.session.status, ResearchSession.Status.COMPLETED)
        self.assertEqual(
            self.session.summary,
            "Research completed successfully.",
        )
        self.assertIsNotNone(run.completed_at)

    @patch("research.services.run.ResearchAnalyzer")
    @patch("research.services.run.WebResearchService")
    def test_collection_failure_marks_run_failed(
        self, web_service_class, analyzer_class
    ):
        web_service_class.return_value.collect_for_session.side_effect = (
            ValueError("Simulated collection failure")
        )

        with self.assertRaisesMessage(
            ValueError,
            "Simulated collection failure",
        ):
            ResearchRunService().execute(self.session)

        self.session.refresh_from_db()

        run = ResearchRun.objects.get(session=self.session)

        self.assertEqual(run.status, ResearchRun.Status.FAILED)
        self.assertEqual(
            run.error_message,
            "Simulated collection failure",
        )
        self.assertEqual(self.session.status, ResearchSession.Status.FAILED)
        self.assertIsNotNone(run.completed_at)

    @patch("research.services.run.ResearchAnalyzer")
    @patch("research.services.run.WebResearchService")
    def test_successful_run_saves_findings(
        self, web_service_class, analyzer_class
    ):
        web_service_class.return_value.collect_for_session.return_value = []

        analyzer_class.return_value.analyze.return_value = {
            "summary": "Audience research summary.",
            "findings": [
                {
                    "finding_type": "problem",
                    "topic": "Time management",
                    "finding": "The audience struggles to manage time.",
                    "audience": "Small business owners",
                    "why_it_matters": "They need simpler workflows.",
                    "limitations": "Based on limited evidence.",
                    "related_questions": ["How can tasks be automated?"],
                    "content_opportunities": ["A productivity guide"],
                    "evidence": "Repeated audience feedback.",
                    "confidence": "high",
                    "importance": 8,
                }
            ],
        }

        run = ResearchRunService().execute(self.session)

        from research.models import ResearchFinding

        finding = ResearchFinding.objects.get(run=run)

        self.assertEqual(finding.topic, "Time management")
        self.assertEqual(finding.confidence, "high")
        self.assertEqual(finding.importance, 8)
        self.assertEqual(
            finding.related_questions,
            ["How can tasks be automated?"],
        )
        self.assertEqual(run.findings.count(), 1)

    @patch("research.services.run.ResearchAnalyzer")
    @patch("research.services.run.WebResearchService")
    def test_analyzer_failure_marks_run_failed(
        self, web_service_class, analyzer_class
    ):
        web_service_class.return_value.collect_for_session.return_value = []
        analyzer_class.return_value.analyze.side_effect = RuntimeError(
            "Simulated analyzer failure"
        )

        with self.assertRaisesMessage(
            RuntimeError,
            "Simulated analyzer failure",
        ):
            ResearchRunService().execute(self.session)

        self.session.refresh_from_db()
        run = ResearchRun.objects.get(session=self.session)

        self.assertEqual(run.status, ResearchRun.Status.FAILED)
        self.assertEqual(
            run.stage,
            ResearchRun.Stage.FAILED,
        )
        self.assertEqual(
            run.error_message,
            "Simulated analyzer failure",
        )
        self.assertEqual(
            self.session.status,
            ResearchSession.Status.FAILED,
        )
        self.assertIsNotNone(run.completed_at)

    def test_each_run_keeps_its_recorded_depth(self):
        first_run = ResearchRun.objects.create(
            session=self.session,
            depth=ResearchSession.Depth.QUICK,
        )

        self.session.depth = ResearchSession.Depth.DEEP
        self.session.save(update_fields=["depth"])

        first_run.refresh_from_db()

        second_run = ResearchRun.objects.create(
            session=self.session,
            depth=self.session.depth,
        )

        self.assertEqual(first_run.depth, ResearchSession.Depth.QUICK)
        self.assertEqual(second_run.depth, ResearchSession.Depth.DEEP)

    def test_invalid_depth_is_not_a_valid_choice(self):
        valid_depths = ResearchSession.Depth.values

        self.assertIn(ResearchSession.Depth.QUICK, valid_depths)
        self.assertIn(ResearchSession.Depth.STANDARD, valid_depths)
        self.assertIn(ResearchSession.Depth.DEEP, valid_depths)
        self.assertNotIn("ultra", valid_depths)
