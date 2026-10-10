from django.utils import timezone

from research.models import ResearchFinding, ResearchRun
from research.services.analyzer import ResearchAnalyzer
from research.services.web import WebResearchService


class ResearchRunService:

    def _update_stage(self, run, stage, message):
        run.stage = stage
        run.stage_message = message
        run.save(
            update_fields=[
                "stage",
                "stage_message",
            ]
        )

    def execute(self, session):

        run = ResearchRun.objects.create(
            session=session,
            depth=session.depth,
            status=ResearchRun.Status.RUNNING,
            stage=ResearchRun.Stage.PLANNING,
            stage_message="Planning your research...",
            started_at=timezone.now(),
        )

        session.status = session.Status.RESEARCHING
        session.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        try:

            # -------------------------------------------------
            # 1. PLANNING
            # -------------------------------------------------

            self._update_stage(
                run,
                ResearchRun.Stage.PLANNING,
                "Planning research angles...",
            )


            # -------------------------------------------------
            # 2. SEARCHING / COLLECTING
            # -------------------------------------------------

            self._update_stage(
                run,
                ResearchRun.Stage.SEARCHING,
                "Searching for relevant information...",
            )

            web_service = WebResearchService()

            items = web_service.collect_for_session(
                session=session,
                run=run,
            )


            self._update_stage(
                run,
                ResearchRun.Stage.COLLECTING,
                "Collecting and organizing research evidence...",
            )

            run.result_count = len(items)

            run.save(
                update_fields=[
                    "result_count",
                ]
            )


            # -------------------------------------------------
            # 3. ANALYZING
            # -------------------------------------------------

            self._update_stage(
                run,
                ResearchRun.Stage.ANALYZING,
                "Analyzing the research evidence...",
            )

            analyzer = ResearchAnalyzer()

            analysis = analyzer.analyze(
                session=session,
                items=items,
            )


            # -------------------------------------------------
            # 4. BUILDING INTELLIGENCE
            # -------------------------------------------------

            self._update_stage(
                run,
                ResearchRun.Stage.BUILDING,
                "Building research intelligence...",
            )


            session.summary = analysis["summary"]

            item_by_id = {
                item.pk: item
                for item in items
            }

            for finding in analysis["findings"]:
                evidence_item_ids = finding.get(
                    "evidence_item_ids",
                    [],
                )

                supporting_items = [
                    item_by_id[item_id]
                    for item_id in evidence_item_ids
                    if item_id in item_by_id
                ]

                saved_finding = ResearchFinding.objects.create(
                    session=session,
                    run=run,
                    research_item=(
                        supporting_items[0]
                        if supporting_items
                        else None
                    ),
                    finding_type=finding["finding_type"],
                    topic=finding.get("topic", ""),
                    finding=finding["finding"],
                    audience=finding.get("audience", ""),
                    why_it_matters=finding.get("why_it_matters", ""),
                    limitations=finding.get("limitations", ""),
                    related_questions=finding.get(
                        "related_questions",
                        [],
                    ),
                    content_opportunities=finding.get(
                        "content_opportunities",
                        [],
                    ),
                    evidence=finding.get("evidence", ""),
                    confidence=finding["confidence"],
                    importance=finding["importance"],
                )

                saved_finding.supporting_items.set(supporting_items)


            # -------------------------------------------------
            # 5. COMPLETE
            # -------------------------------------------------

            run.status = ResearchRun.Status.COMPLETED

            run.stage = ResearchRun.Stage.COMPLETED

            run.stage_message = "Research complete."

            run.completed_at = timezone.now()

            run.save(
                update_fields=[
                    "search_count",
                    "result_count",
                    "status",
                    "stage",
                    "stage_message",
                    "completed_at",
                ]
            )


            session.status = session.Status.COMPLETED

            session.save(
                update_fields=[
                    "summary",
                    "status",
                    "updated_at",
                ]
            )


            return run


        except Exception as exc:

            # ---------------------------------------------
            # FAILED
            # ---------------------------------------------

            run.status = ResearchRun.Status.FAILED

            run.stage = ResearchRun.Stage.FAILED

            run.stage_message = "Research failed."

            run.error_message = str(exc)

            run.completed_at = timezone.now()

            run.save(
                update_fields=[
                    "search_count",
                    "result_count",
                    "status",
                    "stage",
                    "stage_message",
                    "error_message",
                    "completed_at",
                ]
            )


            session.status = session.Status.FAILED

            session.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )


            raise