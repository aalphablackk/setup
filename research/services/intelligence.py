from datetime import timedelta

from django.utils import timezone

from research.models import ResearchFinding


class ResearchIntelligenceService:
    """
    Calculates which research findings matter most right now.

    This service does not modify or delete findings.
    It only ranks the existing research knowledge.
    """

    CONFIDENCE_SCORES = {
        "high": 1.0,
        "medium": 0.7,
        "low": 0.4,
    }

    def get_what_matters_now(self, session, limit=5):
        findings = list(
            ResearchFinding.objects.filter(
                session=session
            ).select_related("run")
        )

        if not findings:
            return []

        now = timezone.now()

        # Count how often similar topics appear.
        topic_counts = {}

        for finding in findings:
            topic = self._normalize_topic(finding.topic)

            if topic:
                topic_counts[topic] = (
                    topic_counts.get(topic, 0) + 1
                )

        scored_findings = []

        for finding in findings:
            importance_score = (
                finding.importance / 10
            )

            confidence_score = (
                self.CONFIDENCE_SCORES.get(
                    finding.confidence,
                    0.4,
                )
            )

            recency_score = self._recency_score(
                finding.created_at,
                now,
            )

            repetition_score = self._repetition_score(
                finding,
                topic_counts,
            )

            actionability_score = self._actionability_score(
                finding
            )

            score = (
                importance_score * 0.40
                + confidence_score * 0.20
                + recency_score * 0.15
                + repetition_score * 0.15
                + actionability_score * 0.10
            )

            scored_findings.append(
                {
                    "finding": finding,
                    "score": round(score * 100, 2),
                    "importance_score": round(
                        importance_score * 100,
                        2,
                    ),
                    "confidence_score": round(
                        confidence_score * 100,
                        2,
                    ),
                    "recency_score": round(
                        recency_score * 100,
                        2,
                    ),
                    "repetition_score": round(
                        repetition_score * 100,
                        2,
                    ),
                    "actionability_score": round(
                        actionability_score * 100,
                        2,
                    ),
                }
            )

        scored_findings.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored_findings[:limit]

    def _normalize_topic(self, topic):
        if not topic:
            return ""

        return " ".join(
            topic.lower().strip().split()
        )

    def _recency_score(self, created_at, now):
        if not created_at:
            return 0.0

        age = now - created_at

        if age <= timedelta(days=1):
            return 1.0

        if age <= timedelta(days=7):
            return 0.9

        if age <= timedelta(days=30):
            return 0.75

        if age <= timedelta(days=90):
            return 0.5

        return 0.25

    def _repetition_score(
        self,
        finding,
        topic_counts,
    ):
        topic = self._normalize_topic(
            finding.topic
        )

        count = topic_counts.get(topic, 1)

        if count >= 5:
            return 1.0

        if count >= 4:
            return 0.9

        if count >= 3:
            return 0.8

        if count >= 2:
            return 0.65

        return 0.4

    def _actionability_score(self, finding):
        opportunities = (
            finding.content_opportunities or []
        )

        questions = (
            finding.related_questions or []
        )

        score = 0.4

        if opportunities:
            score += 0.3

        if questions:
            score += 0.2

        if finding.why_it_matters:
            score += 0.1

        return min(score, 1.0)